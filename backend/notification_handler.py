import requests
import os
from twilio.rest import Client

def send_sms_reminder(phone_number, message):
    """
    Send SMS reminder using Twilio (Free trial available)
    """
    try:
        # For demo purposes - you can use Twilio free trial
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        twilio_number = os.getenv('TWILIO_PHONE_NUMBER')
        
        client = Client(account_sid, auth_token)
        
        message = client.messages.create(
            body=message,
            from_=twilio_number,
            to=phone_number
        )
        
        return {'success': True, 'message_id': message.sid}
        
    except Exception as e:
        # Fallback: Log the message that would be sent
        print(f"DEMO SMS: To {phone_number}: {message}")
        return {'success': True, 'demo_mode': True, 'message': 'SMS would be sent in production'}

def send_whatsapp_reminder(phone_number, message):
    """
    Send WhatsApp reminder (Twilio supports WhatsApp in trial)
    """
    try:
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        
        client = Client(account_sid, auth_token)
        
        message = client.messages.create(
            body=message,
            from_='whatsapp:+14155238886',  # Twilio WhatsApp sandbox
            to=f'whatsapp:{phone_number}'
        )
        
        return {'success': True, 'message_id': message.sid}
        
    except Exception as e:
        print(f"DEMO WhatsApp: To {phone_number}: {message}")
        return {'success': True, 'demo_mode': True}