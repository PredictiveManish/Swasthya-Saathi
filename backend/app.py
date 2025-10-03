from flask import Flask, request, jsonify
from flask_cors import CORS
from gemini_handler import analyze_symptoms
from hospital_finder import find_nearest_hospitals
from ayushman_checker import check_ayushman_eligibility
from data_manager import data_manager
import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
from twilio.rest import Client
# Load environment variables from root directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

app = Flask(__name__)
CORS(app)

# Check if Gemini API key is loaded
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    print(f"Gemini API Key loaded: {GEMINI_API_KEY[:10]}...")
else:
    print("Gemini API Key not found!")

# Twilio Configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

# Initialize Twilio client
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    print("✅ Twilio SMS service configured successfully")
else:
    print("❌ Twilio credentials not found")
    twilio_client = None

@app.route('/api/send-sms', methods=['POST'])
def send_sms():
    """
    Send SMS via Twilio
    """
    try:
        data = request.get_json()
        to_number = data.get('to')
        message = data.get('message')
        
        if not to_number or not message:
            return jsonify({'success': False, 'error': 'Missing phone number or message'}), 400
        
        print(f"📱 Attempting to send SMS to: {to_number}")
        print(f"💬 Message: {message}")
        
        # Check if Twilio is configured
        if not twilio_client:
            print("❌ Twilio not configured - running in demo mode")
            return jsonify({
                'success': True, 
                'demo_mode': True,
                'message': 'SMS would be sent in production',
                'to': to_number,
                'message_content': message
            })
        
        # Send SMS via Twilio
        message = twilio_client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=to_number
        )
        
        print(f"✅ SMS sent successfully! SID: {message.sid}")
        return jsonify({
            'success': True,
            'message_sid': message.sid,
            'to': to_number,
            'status': message.status
        })
        
    except Exception as e:
        print(f"❌ SMS sending failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'demo_fallback': True
        }), 500

@app.route('/api/send-bulk-sms', methods=['POST'])
def send_bulk_sms():
    """
    Send SMS to multiple numbers
    """
    try:
        data = request.get_json()
        phone_numbers = data.get('phone_numbers', [])
        message = data.get('message')
        
        if not phone_numbers or not message:
            return jsonify({'success': False, 'error': 'Missing phone numbers or message'}), 400
        
        results = []
        
        for phone_number in phone_numbers:
            try:
                if twilio_client:
                    # Send actual SMS
                    sent_message = twilio_client.messages.create(
                        body=message,
                        from_=TWILIO_PHONE_NUMBER,
                        to=phone_number
                    )
                    results.append({
                        'phone': phone_number,
                        'success': True,
                        'message_sid': sent_message.sid,
                        'status': sent_message.status
                    })
                else:
                    # Demo mode
                    results.append({
                        'phone': phone_number,
                        'success': True,
                        'demo_mode': True,
                        'status': 'queued'
                    })
                    
            except Exception as e:
                results.append({
                    'phone': phone_number,
                    'success': False,
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'results': results,
            'total_sent': len([r for r in results if r['success']])
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/')
def home():
    """Root endpoint - returns API status"""
    return jsonify({
        "message": "Swasthya Saathi AI Triage API is running!",
        "status": "active",
        "timestamp": datetime.now().isoformat(),
        "gemini_configured": bool(GEMINI_API_KEY),
        "endpoints": {
            "triage": "POST /triage",
            "health": "GET /health",
            "hospitals": "GET /hospitals"
        }
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "service": "Swasthya Saathi Backend",
        "gemini_status": "configured" if GEMINI_API_KEY else "not_configured"
    })

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
        user_phone = data.get('user_phone', '')
        
        print(f"Received symptoms: {symptoms}")
        
        if not symptoms:
            return jsonify({"error": "Symptoms are required"}), 400
        
        # Step 1: Analyze symptoms with Gemini
        triage_result = analyze_symptoms(symptoms, language)
        
        # Step 2: Find hospitals if needed
        hospitals = []
        if triage_result['severity'] in ['Emergency', 'OPD Visit']:
            hospitals = find_nearest_hospitals(
                user_location.get('lat', 28.6139),
                user_location.get('lng', 77.2090),
                ayushman_card
            )
        
        # Step 3: Save to history
        user_data = {
            'phone': user_phone,
            'location': user_location,
            'ayushman_card': ayushman_card
        }
        session_id = data_manager.save_triage_record(user_data, symptoms, triage_result)
        
        # Step 4: Prepare response
        response = {
            'success': True,
            'session_id': session_id,
            'severity': triage_result['severity'],
            'advice': triage_result['advice'],
            'reasoning': triage_result['reasoning'],
            'hospitals': hospitals[:5],
            'ayushman_eligible': ayushman_card,
            'timestamp': datetime.now().isoformat(),
            'gemini_used': bool(GEMINI_API_KEY)
        }
        
        print(f"Triage result: {triage_result['severity']}")
        return jsonify(response)
        
    except Exception as e:
        print(f"Error in triage: {str(e)}")
        return jsonify({
            'error': 'Analysis failed',
            'severity': 'Unknown',
            'advice': 'Please consult a doctor directly',
            'details': str(e)
        }), 500

@app.route('/hospitals', methods=['GET'])
def get_hospitals():
    """Get list of hospitals"""
    try:
        hospitals = find_nearest_hospitals(28.6139, 77.2090, False)
        return jsonify({
            'hospitals': hospitals,
            'count': len(hospitals)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ayushman/check', methods=['POST'])
def check_ayushman():
    """Check Ayushman card eligibility"""
    try:
        data = request.get_json()
        card_number = data.get('card_number')
        result = check_ayushman_eligibility(card_number)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Swasthya Saathi AI Triage Server...")
    print("Local URL: http://127.0.0.1:5000")
    print("Network URL: http://192.168.10.160:5000")
    print(f"Gemini API: {'Configured' if GEMINI_API_KEY else 'Not Configured'}")
    print("Available Endpoints:")
    print("   GET  /              - API status")
    print("   GET  /health        - Health check") 
    print("   POST /triage        - Analyze symptoms")
    print("   GET  /hospitals     - List hospitals")
    print("   POST /ayushman/check - Verify Ayushman card")
    app.run(debug=True, host='0.0.0.0', port=5000)