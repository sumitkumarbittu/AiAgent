from flask import Flask, request, jsonify, render_template
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import logging
from datetime import datetime
from gemini_helper import generate_alert
from gemini_helper_batch import generate_suggestions, format_suggestions_html
import dash
from dashboard import create_dashboard
from feedback_manager import add_feedback, add_batch_feedback, get_all_feedback
from alert import send_alert
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)  # Enable CORS for all routes
# Attach Dash to the existing Flask app
dash_app = create_dashboard(app)  # Attach Dash to the existing Flask app


# API Configuration
FASTAPI_URL = "http://localhost:8000"  # FastAPI service URL
TIMEOUT = 10  # seconds

# Health check for the FastAPI service
def check_fastapi_health():
    try:
        response = requests.get(f"{FASTAPI_URL}/health", timeout=TIMEOUT)
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        logger.error(f"FastAPI health check failed: {str(e)}")
        return False

# Format API response
def format_sentiment_response(text, result):
    """Format the sentiment analysis response"""
    sentiment = str(result.get('sentiment', 'neutral')).lower()
    score = float(result.get('score', 0.5))
    
    # Ensure score is between 0 and 1
    score = max(0, min(1, score))
    
    return {
        'text': text,
        'sentiment': sentiment,
        'score': score,
        'timestamp': datetime.utcnow().isoformat()
    }

@app.route('/')
def index():
    return app.send_static_file('index.html')

# Serve static files from the current directory
@app.route('/<path:path>')
def serve_static(path):
    return app.send_static_file(path)

@app.route('/analyze/single', methods=['POST'])
def analyze_single():
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        logger.info(f"Analyzing text: {text[:100]}...")
        
        # Check if FastAPI service is running
        if not check_fastapi_health():
            error_msg = "Sentiment analysis service is not available"
            logger.error(error_msg)
            return jsonify({"error": error_msg}), 503
        
        # Call FastAPI predict endpoint
        response = requests.post(
            f"{FASTAPI_URL}/predict",
            json={"text": text},
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )
        response.raise_for_status()
        
        # Format the response
        result = response.json()
        formatted_result = format_sentiment_response(text, result)
        
        # Store the analyzed feedback
        try:
            from feedback_manager import add_feedback
            feedback = {
                'text': text,
                'sentiment': formatted_result['sentiment'].capitalize(),
                'score': formatted_result['score'],
                'timestamp': datetime.utcnow().isoformat(),
                'source': 'single_analysis'
            }
            
            # Save the feedback
            result = add_feedback(
                text=feedback['text'],
                sentiment=feedback['sentiment'],
                score=feedback['score'],
                source=feedback['source']
            )
            
            if result is None:
                logger.error(f"Failed to save feedback for text: {text[:50]}...")
            else:
                logger.info(f"Feedback saved: {result.get('text', '')[:50]}... - {result.get('sentiment', 'unknown')}")
                
        except Exception as e:
            logger.error(f"Error saving feedback: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
        
        logger.info(f"Analysis complete. Sentiment: {formatted_result['sentiment']}, Score: {formatted_result['score']}")
        return jsonify(formatted_result)
        
    except requests.exceptions.Timeout:
        error_msg = "Request to sentiment analysis service timed out"
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 504
    except requests.exceptions.RequestException as e:
        error_msg = f"Failed to connect to sentiment analysis service: {str(e)}"
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 502
    except Exception as e:
        error_msg = f"An unexpected error occurred: {str(e)}"
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 500

@app.route('/analyze/batch', methods=['POST'])
def analyze_batch():
    try:
        data = request.get_json()
        texts = data.get('texts', [])
        
        if not texts or not isinstance(texts, list):
            return jsonify({"error": "Invalid input: expected a list of texts"}), 400
        
        logger.info(f"Analyzing batch of {len(texts)} texts")
        
        # Check if FastAPI service is running
        if not check_fastapi_health():
            error_msg = "Sentiment analysis service is not available"
            logger.error(error_msg)
            return jsonify({"error": error_msg}), 503
        
        # Call FastAPI batch predict endpoint
        response = requests.post(
            f"{FASTAPI_URL}/predict_batch",
            json={"texts": texts},
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT * 2  # Allow more time for batch processing
        )
        response.raise_for_status()
        
        # Process and format the results
        results = response.json()
        formatted_results = []
        
        if isinstance(results, list):
            for i, result in enumerate(results):
                text = texts[i] if i < len(texts) else ""
                formatted_result = format_sentiment_response(text, result)
                formatted_results.append(formatted_result)
        
        logger.info(f"Batch analysis complete. Processed {len(formatted_results)} results")
        return jsonify(formatted_results)
        
    except requests.exceptions.Timeout:
        error_msg = "Batch analysis request timed out"
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 504
    except requests.exceptions.RequestException as e:
        error_msg = f"Failed to connect to sentiment analysis service: {str(e)}"
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 502
    except Exception as e:
        error_msg = f"An unexpected error occurred: {str(e)}"
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 500

@app.route('/send-alert', methods=['POST'])
def send_alert_endpoint():
    try:
        data = request.get_json()
        logger.info(f"Received alert request: {data}")
        
        # Validate required fields
        required_fields = ['text', 'sentiment', 'score']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            error_msg = f"Missing required fields: {', '.join(missing_fields)}"
            logger.error(error_msg)
            return jsonify({"error": error_msg}), 400
        
        # Prepare alert data
        alert_data = {
            'text': str(data['text']),
            'sentiment': str(data['sentiment']).lower(),
            'score': float(data['score']),
            'urgency': str(data.get('urgency', 'Medium')).capitalize(),
            'recommendation': str(data.get('recommendation', 'Please review this feedback')),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Log the alert
        logger.info(f"Sending alert: {alert_data}")
        
        try:
            # Send alert using the alert module
            send_alert(
                text=alert_data['text'],
                sentiment=alert_data['sentiment'],
                score=alert_data['score'],
                urgency=alert_data['urgency'],
                recommendation=alert_data['recommendation'],
                recipient=None  # Using default recipient from alert.py
            )
            
            logger.info("Alert sent successfully")
            return jsonify({
                "status": "Alert sent successfully",
                "data": alert_data
            })
            
        except Exception as e:
            error_msg = f"Failed to send alert: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return jsonify({"error": error_msg}), 500
            
    except Exception as e:
        error_msg = f"Invalid request: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return jsonify({"error": error_msg}), 400


# Generate alert using Gemini
@app.route('/api/alerts/gemini', methods=['POST'])
def gemini_alert():
    logger.info("=== Starting Gemini Alert Request ===")
    
    try:
        # Log request details
        logger.info(f"Method: {request.method}")
        logger.info(f"Content-Type: {request.content_type}")
        logger.info(f"Headers: {dict(request.headers)}")
        
        # Check for JSON content
        if not request.is_json:
            error_msg = "Request must be JSON"
            logger.error(error_msg)
            return jsonify({
                "status": "error",
                "error": error_msg,
                "type": "InvalidContentType"
            }), 400
        
        # Parse JSON data
        try:
            data = request.get_json()
            logger.debug(f"Request JSON: {data}")
        except Exception as e:
            error_msg = f"Invalid JSON: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return jsonify({
                "status": "error",
                "error": error_msg,
                "type": "InvalidJSON"
            }), 400
        
        # Validate required fields
        texts = data.get("texts")
        scores = data.get("scores")
        
        logger.info(f"Received {len(texts) if isinstance(texts, list) else 0} texts and {len(scores) if isinstance(scores, list) else 0} scores")
        
        if not texts or not isinstance(texts, list):
            error_msg = "'texts' must be a non-empty list of strings"
            logger.error(error_msg)
            return jsonify({
                "status": "error",
                "error": error_msg,
                "type": "InvalidInput"
            }), 400
            
        if not scores or not isinstance(scores, list):
            error_msg = "'scores' must be a non-empty list of numbers"
            logger.error(error_msg)
            return jsonify({
                "status": "error",
                "error": error_msg,
                "type": "InvalidInput"
            }), 400
            
        if len(texts) != len(scores):
            error_msg = f"'texts' and 'scores' must have the same length. Got {len(texts)} texts and {len(scores)} scores"
            logger.error(error_msg)
            return jsonify({
                "status": "error",
                "error": error_msg,
                "type": "InvalidInput"
            }), 400
        
        logger.info("Input validation passed. Generating alert...")
        
        # Generate the alert
        try:
            alert_message = generate_alert(texts, scores)
            logger.info("Successfully generated alert message")
            
            # Log a preview of the alert
            alert_preview = alert_message[:200] + ('...' if len(alert_message) > 200 else '')
            logger.info(f"Alert preview: {alert_preview}")
            
            # Try to send the alert (but don't fail if this part fails)
            try:
                send_alert(alert_message)
                logger.info("Successfully sent alert to notification system")
            except Exception as alert_error:
                logger.error(f"Warning: Failed to send alert to notification system: {str(alert_error)}", 
                            exc_info=True)
            
            # Return success response
            return jsonify({
                "status": "success",
                "alert": alert_message,
                "texts_processed": len(texts)
            })
            
        except Exception as gen_error:
            error_type = type(gen_error).__name__
            error_details = str(gen_error)
            
            logger.error(f"Error generating alert: {error_type}: {error_details}", 
                        exc_info=True)
            
            # Provide more specific error messages for common issues
            if "API key" in error_details:
                error_msg = "Authentication failed. Please check your Google API key."
            elif "model" in error_details.lower() and "not found" in error_details.lower():
                error_msg = "The specified model was not found. Please check the model name."
            elif "quota" in error_details.lower():
                error_msg = "API quota exceeded. Please check your Google Cloud billing and quotas."
            else:
                error_msg = f"Failed to generate alert: {error_details}"
            
            return jsonify({
                "status": "error",
                "error": error_msg,
                "type": error_type,
                "details": error_details
            }), 500
            
    except Exception as e:
        logger.critical(f"Unexpected error in gemini_alert: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "error": "An unexpected error occurred while processing your request",
            "type": type(e).__name__,
            "details": str(e)
        }), 500
    finally:
        logger.info("=== End of Gemini Alert Request ===")


@app.route('/get_ai_suggestions', methods=['POST'])
def get_ai_suggestions():
    try:
        data = request.get_json()
        complaints = data.get('complaints', [])
        
        if not complaints or not isinstance(complaints, list):
            return jsonify({"error": "Invalid input: expected a list of complaints"}), 400
            
        # Generate suggestions for each complaint
        suggestions = generate_suggestions(complaints)
        
        # Format the response as HTML
        html_response = format_suggestions_html(suggestions)
        
        return jsonify({
            'html': html_response,
            'count': len(suggestions)
        })
        
    except Exception as e:
        logger.error(f"Error generating AI suggestions: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Failed to generate suggestions',
            'details': str(e)
        }), 500


        # Optional: redirect or note that dashboard is at /dashboard/
        @app.route('/dashboard/')
        def dashboard_redirect():
            return dash_app.index()

# Feedback API Endpoints
@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        sentiment = data.get('sentiment', '').strip().capitalize()
        
        if not text or sentiment not in ['Positive', 'Negative']:
            return jsonify({'error': 'Invalid input'}), 400
            
        feedback = add_feedback(text, sentiment)
        return jsonify(feedback), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/feedback/batch', methods=['POST'])
def submit_batch_feedback():
    try:
        data = request.get_json()
        if not isinstance(data, dict) or 'predictions' not in data:
            return jsonify({'error': 'Invalid batch format'}), 400
            
        count = add_batch_feedback(data['predictions'])
        return jsonify({'message': f'Added {count} feedback items'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/feedback', methods=['GET'])
def get_feedback():
    try:
        feedback = get_all_feedback()
        return jsonify(feedback)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
