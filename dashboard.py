import dash
from dash import html, dcc, dash_table, Input, Output, State, ctx

import plotly.express as px
import pandas as pd
import numpy as np
import io
import base64
import json
import os

# ----------------------
# Data Loading
# ----------------------
def load_feedback_data():
    """Load feedback data from JSON file"""
    try:
        if os.path.exists('feedback_data.json'):
            with open('feedback_data.json', 'r') as f:
                data = json.load(f)
                # Ensure we're returning a list of feedback items
                if isinstance(data, dict) and 'feedback' in data:
                    return data['feedback']
                elif isinstance(data, list):
                    return data
                return []
        return []
    except json.JSONDecodeError:
        print("Error: feedback_data.json contains invalid JSON. Resetting to empty list.")
        with open('feedback_data.json', 'w') as f:
            json.dump({"feedback": []}, f)
        return []
    except Exception as e:
        print(f"Error loading feedback data: {e}")
        return []

# Convert feedback data to DataFrame
def get_feedback_df():
    """Convert feedback data to pandas DataFrame"""
    feedback = load_feedback_data()
    
    if not feedback:
        return pd.DataFrame(columns=["text", "sentiment", "source", "timestamp"])
    
    try:
        df = pd.DataFrame(feedback)
        
        # Ensure required columns exist
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Ensure text and sentiment columns exist
        if 'text' not in df.columns:
            df['text'] = ''
        if 'sentiment' not in df.columns:
            df['sentiment'] = 'Neutral'
            
        return df
    except Exception as e:
        print(f"Error creating DataFrame: {e}")
        return pd.DataFrame(columns=["text", "sentiment", "source", "timestamp"])

# Load initial data
data = get_feedback_df()

# ----------------------
# Dash App Factory
# ----------------------
def create_dashboard(server):
    app_dash = dash.Dash(
        __name__,
        server=server,
        url_base_pathname="/dashboard/",
        suppress_callback_exceptions=True,
    )

    # ----------------------
    # Helper functions
    # ----------------------
    def create_pie(df):
        if df.empty:
            return px.pie(names=["No Data"], values=[1], title="Sentiment Distribution")
        return px.pie(
            df,
            names="sentiment",
            color="sentiment",
            color_discrete_map={"Positive":"#28a745","Negative":"#dc3545","Neutral":"#6c757d"},
            title="Sentiment Distribution"
        ).update_traces(textposition='inside', textinfo='percent+label')

    fig_pie = create_pie(data)

    # Trend chart data
    trend_df = pd.DataFrame({
        "Date": pd.date_range("2025-01-01", periods=5, freq="D"),
        "Positive": [2, 3, 4, 5, 6],
        "Negative": [1, 2, 1, 2, 1]
    })

    # Convert Date column to NumPy array to prevent FutureWarning
    trend_df["Date"] = np.array(trend_df["Date"])

    # Create line chart
    fig_trend = px.line(
        trend_df,
        x="Date",
        y=["Positive", "Negative"],
        markers=True,
        title="Sentiment Trend Over Time"
    )

    # Customize chart layout
    fig_trend.update_layout(
        paper_bgcolor="#f8f9fa",
        legend=dict(title="Sentiment")
    )
    # ----------------------
    # Add auto-refresh interval (5 seconds)
    app_dash.layout = html.Div([
        dcc.Interval(
            id='interval-component',
            interval=5*1000,  # 5 seconds
            n_intervals=0
        ),
        
        # Header
        html.Div([
            html.H1("📊 AI Sentiment Dashboard", className="dashboard-title"),
            html.P("Interactive insights, trends & feedback analysis", className="dashboard-subtitle")
        ], className="header-section"),
        
        # KPI Cards
        html.Div([
            html.Div([
                html.H6("Total Feedback", className="card-title"),
                html.H2(id="total-feedback", children="0", className="card-value"),
            ], className="kpi-card", style={"background": "linear-gradient(45deg,#0d6efd,#6610f2)","color": "white"}),
            html.Div([
                html.H6("Positive", className="card-title"),
                html.H2(id="positive-feedback", children="0", className="card-value"),
            ], className="kpi-card", style={"background": "linear-gradient(45deg,#28a745,#198754)","color": "white"}),
            html.Div([
                html.H6("Negative", className="card-title"),
                html.H2(id="negative-feedback", children="0", className="card-value"),
            ], className="kpi-card", style={"background": "linear-gradient(45deg,#dc3545,#a71d2a)","color": "white"}),
        ], className="kpi-container"),
        
        # Charts
        html.Div([
            html.Div([dcc.Graph(id="pie-chart")], className="chart-container"),
        ], className="charts-row"),
        
        # Action Buttons
        html.Div([
            html.Div([
                html.Button("Select All", id="select-all-btn", n_clicks=0, className="btn btn-primary mx-2"),
                html.Button("Deselect All", id="deselect-all-btn", n_clicks=0, className="btn btn-secondary mx-2")
            ], style={"textAlign": "center", "marginBottom": "20px"})
        ]),
        
        # Feedback Table
        html.Div([
            dash_table.DataTable(
                id="feedback-table",
                columns=[
                    {"name": "Feedback", "id": "Feedback"},
                    {"name": "Sentiment", "id": "Sentiment"},
                    {"name": "Date", "id": "Date"}
                ],
                data=[],
                page_size=10,
                filter_action="native",
                sort_action="native",
                sort_mode="multi",
                row_selectable="multi",
                selected_rows=[],
                style_header={
                    "backgroundColor": "#343a40",
                    "color": "white",
                    "fontWeight": "bold",
                    "textAlign": "center"
                },
                style_cell={
                    "textAlign": "left",
                    "padding": "10px",
                    "backgroundColor": "#f8f9fa",
                    "fontSize": "14px"
                },
                style_data_conditional=[
                    {"if": {"filter_query": "{Sentiment} = 'Negative'"},
                     "backgroundColor": "#f8d7da", "color": "#721c24", "fontWeight": "bold"},
                    {"if": {"filter_query": "{Sentiment} = 'Positive'"},
                     "backgroundColor": "#d4edda", "color": "#155724", "fontWeight": "bold"},
                    {"if": {"state": "active"}, "backgroundColor": "#ffeeba", "color": "#856404"},
                    {"if": {"state": "selected"}, "backgroundColor": "#cce5ff", "color": "#004085"},
                ],
                style_as_list_view=True,
            )
        ], className="table-section"),
    ], className="dashboard-container")
    
    # 2️⃣ Update table & KPI cards from feedback data
    @app_dash.callback(
        Output("feedback-table", "data"),
        Output("total-feedback", "children"),
        Output("positive-feedback", "children"),
        Output("negative-feedback", "children"),
        Output("pie-chart", "figure"),
        Input('interval-component', 'n_intervals')
    )
    def update_table(n_intervals):
        try:
            print("\n--- Updating dashboard data ---")
            
            # Get data from feedback file
            print("Loading feedback data...")
            df = get_feedback_df()
            print(f"Loaded {len(df)} feedback entries")
            
            if not df.empty:
                print("Sample data:", df[['text', 'sentiment']].head().to_dict('records'))
            
            # Calculate metrics
            total = len(df)
            positive = len(df[df['sentiment'].str.lower() == 'positive']) if not df.empty else 0
            negative = len(df[df['sentiment'].str.lower() == 'negative']) if not df.empty else 0
            
            print(f"Metrics - Total: {total}, Positive: {positive}, Negative: {negative}")
            
            # Create pie chart data
            if not df.empty and 'sentiment' in df.columns:
                print("Creating pie chart...")
                sentiment_counts = df['sentiment'].value_counts()
                print("Sentiment counts:", sentiment_counts.to_dict())
                
                fig = px.pie(
                    values=sentiment_counts.values,
                    names=sentiment_counts.index,
                    title='Sentiment Distribution',
                    color=sentiment_counts.index,
                    color_discrete_map={
                        'Positive': '#28a745',
                        'Negative': '#dc3545',
                        'Neutral': '#6c757d'
                    }
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
            else:
                print("No data or sentiment column not found, using empty pie chart")
                fig = px.pie(names=["No Data"], values=[1], title="Sentiment Distribution")
            
            # Prepare table data
            if not df.empty:
                print("Preparing table data...")
                if 'timestamp' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                table_data = df.rename(columns={
                    'text': 'Feedback',
                    'sentiment': 'Sentiment',
                    'timestamp': 'Date'
                }).to_dict('records')
                print(f"Prepared {len(table_data)} table rows")
            else:
                print("No data for table")
                table_data = []
            
            print("--- Update complete ---\n")
            return table_data, total, positive, negative, fig
            
        except Exception as e:
            print(f"Error in update_table: {str(e)}")
            import traceback
            traceback.print_exc()
            return [], 0, 0, 0, px.pie(names=["Error"], values=[1], title="Error Loading Data")

    # 3️⃣ Select / Deselect all rows
    @app_dash.callback(
        Output("feedback-table", "selected_rows"),
        Input("select-all-btn", "n_clicks"),
        Input("deselect-all-btn", "n_clicks"),
        State("feedback-table", "data")
    )
    def select_deselect_all(select_all_clicks, deselect_all_clicks, table_data):
        if ctx.triggered_id == "select-all-btn":
            return list(range(len(table_data)))
        elif ctx.triggered_id == "deselect-all-btn":
            return []
        return []

    return app_dash
