from flask import Flask, request, jsonify
from flask_cors import CORS
from gemini_handler import analyze_symptoms
from hospital_finder import find_nearest_hospitals
from ayushman_checker import check_ayushman_eligibility
from notification_handler import send_notification
from data_manager import data_manager
import json

app = Flask(__name__)
CORS(app)

@app.route('/triage', methods=['POST'])
def triage_symptoms():
    try:
        data = request.get_json()
        symptoms = data.get('symptoms', '')
        language = data.get('language', 'en')
        ayushman_card = data.get('ayushman_card', False)
        user_location = data.get('location', {})
        user_phone = data.get('user_phone', '')
        
        print(f"Triage request: {symptoms[:100]}...")
        
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
            'session_id': session_id,
            'severity': triage_result['severity'],
            'advice': triage_result['advice'],
            'reasoning': triage_result['reasoning'],
            'hospitals': hospitals[:5],
            'ayushman_eligible': ayushman_card,
            'timestamp': data_manager.get_current_timestamp()
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Triage error: {str(e)}")
        return jsonify({
            'error': 'Analysis failed',
            'severity': 'Unknown',
            'advice': 'Please consult a doctor directly'
        }), 500

@app.route('/medication/reminder', methods=['POST'])
def set_medication_reminder():
    """Set up medication reminder"""
    data = request.get_json()
    user_phone = data.get('user_phone')
    medication_data = data.get('medication')
    
    if not user_phone or not medication_data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    schedule = data_manager.save_medication_schedule(user_phone, medication_data)
    
    return jsonify({
        'success': True,
        'schedule_id': schedule.get('id'),
        'next_reminder': schedule.get('next_reminder')
    })

@app.route('/history/<user_phone>', methods=['GET'])
def get_user_history(user_phone):
    """Get user's triage history"""
    history = data_manager.load_data('triage_history.json', [])
    user_history = [h for h in history if h.get('user_data', {}).get('phone') == user_phone]
    
    return jsonify({
        'history': user_history[-10:]  # Last 10 records
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)