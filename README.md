# Sentiment Analysis Web Application with Dashboard & Alert System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.0.1-green.svg)](https://flask.palletsprojects.com/)
[![Plotly](https://img.shields.io/badge/Plotly-Dash-ff69b4.svg)](https://plotly.com/dash/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive web application for real-time sentiment analysis with an interactive dashboard and integrated alert system. This tool helps businesses and individuals monitor, analyze, and visualize sentiment in textual data.

## 🌟 Key Features

### Text Analysis
- **Single Text Analysis**: Get immediate sentiment analysis for individual text inputs
- **Batch Processing**: Analyze multiple texts simultaneously for efficient processing
- **Sentiment Scoring**: Detailed sentiment scores with confidence levels
- **Real-time Processing**: Quick analysis with minimal latency

### Interactive Dashboard
- **Sentiment Distribution**: Visual pie chart showing sentiment breakdown
- **Trend Analysis**: Track sentiment trends over time
- **Data Table**: View and manage all feedback entries
- **Real-time Updates**: Auto-refreshing interface for latest data

### Alert System
- **Instant Notifications**: Real-time alerts for important sentiment findings
- **Customizable Thresholds**: Set custom thresholds for alerts
- **Multiple Alert Types**: Different levels based on sentiment severity

### User Experience
- **Responsive Design**: Fully responsive interface that works on all devices
- **Interactive Visualizations**: Built with Plotly Dash for rich, interactive charts
- **Intuitive UI**: Clean, modern interface with Bootstrap 5
- **Real-time Feedback**: Instant analysis and visualization updates

### Technical Features
- **RESTful API**: Well-documented endpoints for all features
- **Data Persistence**: JSON-based storage for feedback data
- **Modular Design**: Clean separation of concerns with dedicated modules
- **Comprehensive Logging**: Detailed logging for debugging and monitoring
- **Asynchronous Processing**: Non-blocking operations for better performance

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (for version control)
- Modern web browser (Chrome, Firefox, Edge, or Safari)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/sentiment-analysis-app.git
   cd sentiment-analysis-app
   ```

2. **Set up a virtual environment**
   ```bash
   # For Windows
   python -m venv venv
   .\venv\Scripts\activate

   # For macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=sqlite:///app.db
   DEBUG=True
   ```

5. **Initialize the feedback data file**
   ```bash
   echo '{"feedback": []}' > feedback_data.json
   ```

## 🏃‍♂️ Running the Application

### Development Mode
```bash
# Start the application
python app.py
```

### Access the Application
Open your browser and navigate to:
- Main Application: `http://localhost:5001`
- Dashboard: `http://localhost:5001/dashboard/`

## 📊 Using the Dashboard

The interactive dashboard provides:
- Real-time sentiment analysis visualization
- Historical trend analysis
- Feedback management interface
- Export capabilities for analysis results

### Key Dashboard Features:
1. **Sentiment Distribution**: Pie chart showing sentiment breakdown
2. **Trend Analysis**: Line chart tracking sentiment over time
3. **Feedback Table**: Sortable and searchable data table
4. **Auto-refresh**: Data updates automatically every 5 seconds
```
http://localhost:5001
```

## 🛠️ Configuration

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_APP` | Entry point of the Flask application | `app.py` |
| `FLASK_ENV` | Environment (development/production) | `development` |
| `SECRET_KEY` | Secret key for session management | `None` (required) |
| `DATABASE_URL` | Database connection URL | `sqlite:///app.db` |
| `DEBUG` | Enable/disable debug mode | `False` in production |

### Sentiment Analysis Configuration
The application can be configured to use different sentiment analysis models or adjust sensitivity thresholds in the `config.py` file.

## 📚 API Documentation

### Authentication
All API endpoints (except `/login` and `/register`) require authentication. Include the JWT token in the `Authorization` header:
```
Authorization: Bearer <your_token>
```

### Available Endpoints

#### Analysis Endpoints
- `POST /api/analyze` - Analyze single text
  ```json
  {
    "text": "I love this product! It's amazing."
  }
  ```

- `POST /api/analyze/batch` - Analyze multiple texts
  ```json
  {
    "texts": [
      "I love this product!",
      "This is terrible quality.",
      "It's okay, could be better."
    ]
  }
  ```

#### Alert Endpoints
- `POST /api/alerts` - Create a new alert rule
- `GET /api/alerts` - Get all alert rules
- `GET /api/alerts/<id>` - Get specific alert rule
- `PUT /api/alerts/<id>` - Update alert rule
- `DELETE /api/alerts/<id>` - Delete alert rule

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👏 Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- Frontend powered by [Bootstrap 5](https://getbootstrap.com/)
- Icons by [Bootstrap Icons](https://icons.getbootstrap.com/)
- Sentiment analysis powered by [Transformers](https://huggingface.co/transformers/)

## 📧 Contact

For questions or feedback, please reach out to [your-email@example.com](mailto:your-email@example.com)
