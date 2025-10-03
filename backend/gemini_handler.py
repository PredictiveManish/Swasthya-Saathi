import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from root directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    print("Gemini API configured successfully")
else:
    print("GEMINI_API_KEY not found in environment variables")
    print("Please check your .env file in the root directory")

def analyze_symptoms(symptoms, language='en'):
    """
    Analyze symptoms using Google Gemini API
    """
    # Fallback response if Gemini fails
    fallback_response = {
        'severity': 'OPD Visit',
        'advice': 'Please consult a healthcare provider for proper diagnosis.',
        'reasoning': 'AI analysis unavailable - defaulting to doctor consultation'
    }
    
    # Check if API key is available
    if not GEMINI_API_KEY:
        print("Gemini API key not available, using fallback")
        return fallback_response
    
    try:
        # Create the prompt for Gemini
        prompt = f"""
        You are a medical triage AI assistant. Analyze the following symptoms and provide a severity classification with medical reasoning.

        PATIENT SYMPTOMS: {symptoms}

        CLASSIFY INTO ONE OF THESE THREE CATEGORIES:
        - "Emergency": Life-threatening conditions needing immediate care (heart attack, stroke, severe bleeding, difficulty breathing, unconsciousness)
        - "OPD Visit": Non-emergency but requires doctor consultation (persistent fever, ongoing pain, chronic conditions)
        - "Self-care": Mild symptoms that can be managed at home (common cold, minor aches, mild indigestion)

        RESPOND WITH THIS EXACT JSON FORMAT ONLY:
        {{
            "severity": "Emergency/OPD Visit/Self-care",
            "advice": "Specific, actionable medical advice in 2-3 sentences",
            "reasoning": "Medical explanation for this classification in 2-3 sentences"
        }}

        IMPORTANT GUIDELINES:
        - Be medically accurate and cautious
        - When in doubt, recommend higher care level
        - Consider patient safety as top priority
        - Provide clear, practical advice
        - Base reasoning on standard medical triage protocols
        - If symptoms suggest multiple possibilities, choose the most serious one

        Respond only with valid JSON, no additional text or explanations.
        """
        
        print(f"Sending to Gemini API: {symptoms[:100]}...")
        
        # Initialize the model with safety settings
        generation_config = {
            "temperature": 0.5,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 1024,
        }
        
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
        
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        # Generate response
        response = model.generate_content(prompt)
        
        # Extract the response text
        response_text = response.text.strip()
        print(f"Raw Gemini response: {response_text}")
        
        # Clean the response - remove markdown code blocks if present
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif '```' in response_text:
            response_text = response_text.split('```')[1].strip()
        elif response_text.startswith('{') and response_text.endswith('}'):
            # Response is already clean JSON
            pass
        else:
            # Try to extract JSON from text
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                response_text = response_text[start_idx:end_idx]
        
        # Parse JSON response
        result = json.loads(response_text)
        
        # Validate the response structure
        required_fields = ['severity', 'advice', 'reasoning']
        if all(field in result for field in required_fields):
            print(f"Gemini analysis successful: {result['severity']}")
            return {
                'severity': result['severity'],
                'advice': result['advice'],
                'reasoning': result['reasoning']
            }
        else:
            print("Invalid response format from Gemini")
            return fallback_response
            
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Raw response that failed: {response_text}")
        return fallback_response
        
    except Exception as e:
        print(f"Gemini API error: {str(e)}")
        return fallback_response