from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Mock Gemini function (replace with actual API)
def analyze_symptoms(symptoms, language='en'):
    """
    Mock symptom analysis - replace with actual Gemini API
    """
    # Simple symptom analysis logic
    symptoms_lower = symptoms.lower()
    
    # Emergency indicators
    emergency_keywords = ['chest pain', 'difficulty breathing', 'severe bleeding', 'unconscious', 'heart attack', 'stroke']
    # OPD indicators  
    opd_keywords = ['fever', 'cough', 'headache', 'vomiting', 'diarrhea', 'pain']
    
    if any(keyword in symptoms_lower for keyword in emergency_keywords):
        return {
            'severity': 'Emergency',
            'advice': 'Seek immediate medical attention. Go to the nearest emergency department.',
            'reasoning': 'Symptoms indicate a potential medical emergency requiring immediate care.'
        }
    elif any(keyword in symptoms_lower for keyword in opd_keywords):
        return {
            'severity': 'OPD Visit',
            'advice': 'Schedule an appointment with a healthcare provider within 24-48 hours.',
            'reasoning': 'Symptoms require professional medical evaluation but are not immediately life-threatening.'
        }
    else:
        return {
            'severity': 'Self-care',
            'advice': 'Rest, hydrate, and monitor symptoms. Consult doctor if symptoms worsen.',
            'reasoning': 'Symptoms appear mild and can be managed with self-care measures.'
        }

# Mock hospital data
def load_hospitals():
    return [
        {
            "id": 1,
            "name": "City General Hospital",
            "address": "123 Main Street, Delhi",
            "lat": 28.6139,
            "lng": 77.2090,
            "phone": "+91-11-12345678",
            "ayushman": True,
            "distance": 2.1,
            "emergency_services": True
        },
        {
            "id": 2,
            "name": "Community Health Center", 
            "address": "456 Park Avenue, Delhi",
            "lat": 28.6200,
            "lng": 77.2200,
            "phone": "+91-11-87654321",
            "ayushman": True,
            "distance": 3.5,
            "emergency_services": True
        }
    ]

@app.route('/')
def home():
    """Root endpoint - returns API status"""
    return jsonify({
        "message": "Swasthya Saathi AI Triage API is running!",
        "status": "active",
        "endpoints": {
            "triage": "POST /triage",
            "health": "GET /health"
        }
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/triage', methods=['POST', 'GET'])
def triage_symptoms():
    """Main triage endpoint"""
    if request.method == 'GET':
        return jsonify({
            "message": "Send POST request with symptoms data",
            "example_request": {
                "symptoms": "fever and headache for 2 days",
                "language": "en", 
                "ayushman_card": True,
                "location": {"lat": 28.6139, "lng": 77.2090}
            }
        })
    
    try:
        # Get data from frontend
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data received"}), 400
            
        symptoms = data.get('symptoms', '')
        language = data.get('language', 'en')
        ayushman_card = data.get('ayushman_card', False)
        user_location = data.get('location', {})
        
        print(f"🔍 Received symptoms: {symptoms}")
        
        if not symptoms:
            return jsonify({"error": "Symptoms are required"}), 400
        
        # Step 1: Analyze symptoms
        triage_result = analyze_symptoms(symptoms, language)
        
        # Step 2: Find hospitals if needed
        hospitals = []
        if triage_result['severity'] in ['Emergency', 'OPD Visit']:
            hospitals = load_hospitals()
            # Filter by Ayushman if requested
            if ayushman_card:
                hospitals = [h for h in hospitals if h['ayushman']]
        
        # Step 3: Prepare response
        response = {
            'success': True,
            'severity': triage_result['severity'],
            'advice': triage_result['advice'],
            'reasoning': triage_result['reasoning'],
            'hospitals': hospitals[:3],  # Top 3 nearest
            'ayushman_eligible': ayushman_card,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"✅ Triage result: {triage_result['severity']}")
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Error in triage: {str(e)}")
        return jsonify({
            'error': 'Analysis failed',
            'severity': 'Unknown',
            'advice': 'Please consult a doctor directly'
        }), 500

@app.route('/hospitals', methods=['GET'])
def get_hospitals():
    """Get list of hospitals"""
    hospitals = load_hospitals()
    return jsonify({
        'hospitals': hospitals,
        'count': len(hospitals)
    })

if __name__ == '__main__':
    print("🚀 Starting Swasthya Saathi AI Triage Server...")
    print("📍 API URL: http://127.0.0.1:5000")
    print("📍 Local Network: http://192.168.10.160:5000")
    print("📋 Available Endpoints:")
    print("   GET  /          - API status")
    print("   GET  /health    - Health check") 
    print("   POST /triage    - Analyze symptoms")
    print("   GET  /hospitals - List hospitals")
    app.run(debug=True, host='0.0.0.0', port=5000)