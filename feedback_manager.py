import json
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

FEEDBACK_FILE = 'feedback_data.json'

def init_feedback_file():
    """Initialize feedback file if it doesn't exist"""
    logger.debug(f"Initializing feedback file at: {os.path.abspath(FEEDBACK_FILE)}")
    if not os.path.exists(FEEDBACK_FILE):
        logger.info(f"Feedback file not found, creating new one at: {os.path.abspath(FEEDBACK_FILE)}")
        try:
            with open(FEEDBACK_FILE, 'w') as f:
                json.dump({"feedback": []}, f, indent=2)
            logger.info("Successfully created new feedback file")
        except Exception as e:
            logger.error(f"Failed to create feedback file: {str(e)}")
            raise
    # Ensure file has correct structure
    try:
        with open(FEEDBACK_FILE, 'r+') as f:
            data = json.load(f)
            if 'feedback' not in data:
                data = {"feedback": data if isinstance(data, list) else []}
                f.seek(0)
                json.dump(data, f, indent=2)
                f.truncate()
    except (json.JSONDecodeError, FileNotFoundError):
        # If file is corrupted, reset it
        with open(FEEDBACK_FILE, 'w') as f:
            json.dump({"feedback": []}, f, indent=2)

def add_feedback(text, sentiment, source="analysis", score=None):
    """Add a single feedback entry
    
    Args:
        text (str): The feedback text
        sentiment (str): The sentiment (Positive/Negative/Neutral)
        source (str): Source of the feedback (default: 'analysis')
        score (float, optional): Sentiment score between 0 and 1
    """
    try:
        print(f"Adding feedback: {text[:50]}... - {sentiment} (Score: {score})")
        init_feedback_file()
        
        feedback = {
            "text": str(text),
            "sentiment": str(sentiment).capitalize(),
            "source": str(source),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add score if provided
        if score is not None:
            feedback["score"] = float(score)
        
        # Read existing data
        if os.path.exists(FEEDBACK_FILE):
            with open(FEEDBACK_FILE, 'r') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    print("Error: Invalid JSON in feedback file. Resetting...")
                    data = {"feedback": []}
        else:
            data = {"feedback": []}
        
        # Ensure feedback list exists
        if 'feedback' not in data:
            data['feedback'] = []
        
        # Add new feedback
        data['feedback'].append(feedback)
        
        # Write back to file
        temp_file = FEEDBACK_FILE + '.tmp'
        with open(temp_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Atomic write
        if os.name == 'nt':  # Windows
            if os.path.exists(FEEDBACK_FILE):
                os.remove(FEEDBACK_FILE)
            os.rename(temp_file, FEEDBACK_FILE)
        else:  # Unix/Linux
            os.replace(temp_file, FEEDBACK_FILE)
        
        print(f"Successfully added feedback. Total entries: {len(data['feedback'])}")
        return feedback
        
    except Exception as e:
        print(f"Error in add_feedback: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def add_batch_feedback(batch_data, source="batch_analysis"):
    """Add multiple feedback entries from batch analysis"""
    init_feedback_file()
    
    with open(FEEDBACK_FILE, 'r+') as f:
        data = json.load(f)
        
        for item in batch_data:
            feedback = {
                "text": item.get("text", ""),
                "sentiment": item.get("sentiment", ""),
                "source": source,
                "timestamp": datetime.now().isoformat()
            }
            data["feedback"].append(feedback)
        
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()
    
    return len(batch_data)

def get_all_feedback():
    """Retrieve all feedback entries"""
    init_feedback_file()  # Ensure file exists and is properly formatted
    
    try:
        with open(FEEDBACK_FILE, 'r') as f:
            data = json.load(f)
            feedback = data.get("feedback", [])
            # Ensure each entry has required fields
            for item in feedback:
                if 'text' not in item:
                    item['text'] = ''
                if 'sentiment' not in item:
                    item['sentiment'] = 'Neutral'
                if 'source' not in item:
                    item['source'] = 'unknown'
                if 'timestamp' not in item:
                    item['timestamp'] = datetime.now().isoformat()
            return feedback
    except (json.JSONDecodeError, FileNotFoundError):
        return []
