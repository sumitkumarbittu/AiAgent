# gemini_helper.py
import google.generativeai as genai
import os
import logging
from dotenv import load_dotenv
import sys

# Load environment variables from .env
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG to see more detailed logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configure the API key and initialize the model
model = None
try:
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is not set")
    
    logger.info("Configuring Gemini API with the provided key")
    genai.configure(api_key=api_key)
    
    logger.info("Initializing Gemini model")
    model = genai.GenerativeModel('gemini-2.5-flash')
    logger.info("Successfully initialized Gemini model")
    
except Exception as e:
    logger.error(f"Failed to initialize Gemini: {str(e)}", exc_info=True)
    raise

def generate_alert(texts, sentiment_scores):
    """
    Generate a concise alert message using Gemini LLM.
    
    Args:
        texts: List of text strings to analyze
        sentiment_scores: List of sentiment scores corresponding to the texts
        
    Returns:
        str: Generated alert message
    """
    logger.info(f"Starting generate_alert with {len(texts)} texts")
    
    try:
        # Input validation
        if not texts or not isinstance(texts, list) or not all(isinstance(t, str) for t in texts):
            error_msg = f"texts must be a non-empty list of strings, got: {texts}"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        if not sentiment_scores or not isinstance(sentiment_scores, list):
            error_msg = f"sentiment_scores must be a non-empty list, got: {sentiment_scores}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        if len(texts) != len(sentiment_scores):
            error_msg = f"texts and sentiment_scores must have the same length. Got {len(texts)} texts and {len(sentiment_scores)} scores"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Check if model is initialized
        if model is None:
            error_msg = "Gemini model is not initialized. Check your API key and internet connection."
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        # Format the input for better readability
        formatted_input = "\n".join(
            f"Text: {text[:200]}..." + ("" if len(text) <= 200 else "") + 
            f"\nSentiment Score: {score:.2f}\n" 
            for text, score in zip(texts, sentiment_scores)
        )
        
        prompt = f"""
        You are a helpful assistant that analyzes customer feedback and generates 
        concise alert messages for the support team.
        
        Please analyze the following customer feedback and their sentiment scores, 
        then generate a brief alert message highlighting any critical issues:
        
        {formatted_input}
        
        Guidelines:
        - Focus on the most critical issues first
        - Be concise but specific
        - Include any patterns or common themes
        - If there are no critical issues, note that as well
        """
        
        logger.info("Sending request to Gemini API...")
        logger.debug(f"Prompt length: {len(prompt)} characters")
        
        try:
            # Generate the response using the model
            response = model.generate_content(prompt)
            logger.info("Successfully received response from Gemini API")
            
            # Debug: Log basic response info
            logger.debug(f"Response type: {type(response).__name__}")
            
            # Extract the response text based on the response structure
            if hasattr(response, 'text') and response.text:
                result = response.text.strip()
                logger.info("Extracted response text")
                return result
                
            # Handle different response formats
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    if candidate.content.parts:
                        result = candidate.content.parts[0].text.strip()
                        logger.info("Extracted response from candidates")
                        return result
            
            # If we get here, we couldn't extract the response
            error_msg = f"Unexpected response format from Gemini. Response: {response}"
            logger.error(error_msg)
            raise RuntimeError("Unable to process the response from the AI model.")
            
        except Exception as api_error:
            logger.error(f"Gemini API Error: {str(api_error)}", exc_info=True)
            if hasattr(api_error, 'response') and hasattr(api_error.response, 'text'):
                logger.error(f"API Error Response: {api_error.response.text}")
            raise RuntimeError(f"Failed to generate content: {str(api_error)}")
            
    except Exception as e:
        logger.error(f"Error in generate_alert: {str(e)}", exc_info=True)
        raise
