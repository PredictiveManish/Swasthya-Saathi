import google.generativeai as genai
import os
import json

# Configure Gemini API (you'll need to get an API key)
genai.configure(api_key=os.getenv('GEMINI_API_KEY', 'your-api-key-here'))

def analyze_symptoms(symptoms, language='en'):
    """
    Analyze symptoms using Gemini API
    Returns: severity, advice, reasoning
    """
    
    prompt = f"""
    Analyze these symptoms and classify severity into one of these three categories:
    - Self-care: Mild symptoms that can be managed at home
    - OPD Visit: Requires doctor consultation but not emergency
    - Emergency: Needs immediate medical attention
    
    Symptoms: {symptoms}
    
    Respond in this exact JSON format:
    {{
        "severity": "Self-care/OPD Visit/Emergency",
        "advice": "Specific medical advice",
        "reasoning": "Explanation for this classification"
    }}
    
    Be medically accurate and cautious. When in doubt, recommend higher care level.
    """
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        
        # Parse the response
        result_text = response.text.strip()
        
        # Extract JSON from response (Gemini might add extra text)
        if '```json' in result_text:
            result_text = result_text.split('```json')[1].split('```')[0]
        elif '```' in result_text:
            result_text = result_text.split('```')[1]
        
        result = json.loads(result_text)
        
        return {
            'severity': result.get('severity', 'Unknown'),
            'advice': result.get('advice', 'Please consult a doctor'),
            'reasoning': result.get('reasoning', 'Unable to analyze symptoms')
        }
        
    except Exception as e:
        print(f"Gemini API error: {str(e)}")
        return {
            'severity': 'OPD Visit',
            'advice': 'Please consult a healthcare provider for proper diagnosis',
            'reasoning': 'AI analysis unavailable - defaulting to doctor consultation'
        }