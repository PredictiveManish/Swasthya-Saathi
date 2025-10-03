import json
import os
from datetime import datetime

class DataManager:
    def __init__(self):
        self.data_dir = 'data'
        self.ensure_data_directory()
    
    def ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def save_triage_record(self, user_data, symptoms, triage_result):
        """Save triage session to history"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "user_data": user_data,
            "symptoms": symptoms,
            "triage_result": triage_result,
            "session_id": self.generate_session_id()
        }
        
        # Load existing history
        history = self.load_data('triage_history.json', [])
        history.append(record)
        
        # Save updated history
        self.save_data('triage_history.json', history)
        
        return record['session_id']
    
    def save_medication_schedule(self, user_phone, medication_data):
        """Save medication schedule for reminders"""
        schedules = self.load_data('medication_schedules.json', [])
        
        schedule = {
            "user_phone": user_phone,
            "medication": medication_data,
            "created_at": datetime.now().isoformat(),
            "next_reminder": self.calculate_next_reminder(medication_data),
            "completed_doses": 0,
            "missed_doses": 0
        }
        
        schedules.append(schedule)
        self.save_data('medication_schedules.json', schedules)
        
        return schedule
    
    def load_data(self, filename, default=None):
        """Load data from JSON file"""
        try:
            filepath = os.path.join(self.data_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return default if default is not None else {}
    
    def save_data(self, filename, data):
        """Save data to JSON file"""
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def generate_session_id(self):
        """Generate unique session ID"""
        return datetime.now().strftime("%Y%m%d%H%M%S")
    
    def calculate_next_reminder(self, medication_data):
        """Calculate next reminder time based on medication schedule"""
        # Simplified implementation
        from datetime import timedelta
        return (datetime.now() + timedelta(hours=8)).isoformat()

# Global instance
data_manager = DataManager()