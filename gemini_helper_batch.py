import google.generativeai as genai
import os
import logging
from dotenv import load_dotenv
import sys

# Load environment variables from .env
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
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
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    logger.info("Successfully initialized Gemini model")
    
except Exception as e:
    logger.error(f"Failed to initialize Gemini: {str(e)}", exc_info=True)
    raise

def generate_suggestions(complaints):
    """
    Generate AI suggestions for each complaint individually.
    
    Args:
        complaints: List of complaint strings
        
    Returns:
        list: List of dictionaries containing original complaint and AI suggestion
    """
    if not complaints or not isinstance(complaints, list):
        raise ValueError("Input must be a non-empty list of complaint strings")
    
    results = []
    
    for complaint in complaints:
        if not isinstance(complaint, str) or not complaint.strip():
            logger.warning(f"Skipping invalid complaint: {complaint}")
            results.append({
                'complaint': complaint,
                'suggestion': 'Invalid complaint format',
                'error': 'Invalid input'
            })
            continue
            
        try:
            prompt = f"""
            You are a helpful customer support assistant. Please provide a professional and empathetic 
            response to the following customer complaint. Keep the response concise and solution-oriented.
            
            Complaint: "{complaint}"
            
            Suggestion:
            """
            
            response = model.generate_content(prompt)
            
            # Extract the suggestion text
            if hasattr(response, 'text') and response.text:
                suggestion = response.text.strip('"\n ')
            else:
                suggestion = "Unable to generate a suggestion at this time."
                
            results.append({
                'complaint': complaint,
                'suggestion': suggestion
            })
            
        except Exception as e:
            logger.error(f"Error generating suggestion for complaint: {complaint}", exc_info=True)
            results.append({
                'complaint': complaint,
                'suggestion': 'Error generating suggestion',
                'error': str(e)
            })
    
    return results

def format_suggestions_html(suggestions):
    """
    Format the suggestions into an HTML string for display.
    
    Args:
        suggestions: List of suggestion dictionaries
        
    Returns:
        str: HTML formatted string with text and suggestions
    """
    if not suggestions:
        return "<div>No suggestions available</div>"
    
    html_parts = ['<div class="suggestions-container">']
    
    for item in suggestions:
        if 'error' in item:
            html_parts.append(f'<div class="suggestion-error">Error processing: {item["complaint"]}</div>')
        else:
            html_parts.append('<div class="suggestion-item mb-4">')
            html_parts.append(f'<div class="text mb-2">{item["complaint"]}</div>')
            html_parts.append(f'<div class="suggestion p-3 bg-light rounded">\
                <div class="text-muted small mb-1">AI Suggestion:</div>\
                {item["suggestion"]}\
            </div>')
            html_parts.append('</div>')
    
    html_parts.append('</div>')
    return '\n'.join(html_parts)

def get_suggestions_button_html():
    """Return HTML for the suggestions button"""
    return """
    <button id="showSuggestionsBtn" class="btn btn-primary mt-2" 
            onclick="toggleSuggestions()">
        Show AI Suggestions
    </button>
    <div id="suggestionsContainer" style="display: none; margin-top: 15px; padding: 15px; 
                                        border: 1px solid #ddd; border-radius: 5px; 
                                        background-color: #f9f9f9;"></div>
    <script>
    function toggleSuggestions() {
        const container = document.getElementById('suggestionsContainer');
        const button = document.getElementById('showSuggestionsBtn');
        
        if (container.style.display === 'none') {
            // If we're showing suggestions, fetch them if not already loaded
            if (!container.hasAttribute('data-loaded')) {
                container.innerHTML = 'Generating suggestions...';
                
                // Get all complaint texts from the page
                const complaints = Array.from(document.querySelectorAll('.complaint-text'))
                    .map(el => el.textContent.trim())
                    .filter(text => text.length > 0);
                
                // Call the backend to get suggestions
                fetch('/get_ai_suggestions', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ complaints: complaints })
                })
                .then(response => response.json())
                .then(data => {
                    container.innerHTML = data.html;
                    container.setAttribute('data-loaded', 'true');
                })
                .catch(error => {
                    console.error('Error fetching suggestions:', error);
                    container.innerHTML = 'Error loading suggestions. Please try again.';
                });
            }
            container.style.display = 'block';
            button.textContent = 'Hide AI Suggestions';
        } else {
            container.style.display = 'none';
            button.textContent = 'Show AI Suggestions';
        }
    }
    </script>
    """
