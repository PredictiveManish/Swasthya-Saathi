import json
import math
import os
from datetime import datetime

class HospitalFinder:
    def __init__(self):
        self.hospitals = self.load_hospitals()
        self.ayushman_data = self.load_ayushman_data()
    
    def load_hospitals(self):
        """Load hospital data from JSON file"""
        try:
            # Use absolute path
            file_path = os.path.join(os.path.dirname(__file__), 'data', 'hospitals.json')
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"✅ Loaded {len(data.get('hospitals', []))} hospitals")
                return data.get('hospitals', [])
        except FileNotFoundError:
            print("❌ Hospital data file not found, using mock data")
            return self.get_mock_hospitals()
        except Exception as e:
            print(f"❌ Error loading hospitals: {e}")
            return self.get_mock_hospitals()
    
    def load_ayushman_data(self):
        """Load Ayushman hospital data"""
        try:
            file_path = os.path.join(os.path.dirname(__file__), 'data', 'ayushman_hospitals.json')
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"✅ Loaded {len(data.get('ayushman_empaneled', []))} Ayushman hospitals")
                return data
        except FileNotFoundError:
            print("❌ Ayushman hospitals file not found")
            return {"ayushman_empaneled": []}
    
    # ... rest of your existing hospital_finder.py code ...
    
    def get_mock_hospitals(self):
        """Fallback mock data"""
        return [
            {
                "id": 1,
                "name": "Local Government Hospital",
                "type": "Government",
                "address": "Main Road, City Center",
                "lat": 28.6139,
                "lng": 77.2090,
                "phone": "+91-XXX-XXXXXXX",
                "emergency_services": True,
                "ayushman": True,
                "beds": 100,
                "icu_beds": 10,
                "ambulance_service": True,
                "rating": 4.0
            }
        ]
    
    def calculate_distance(self, lat1, lng1, lat2, lng2):
        """Calculate distance between two coordinates in kilometers"""
        # Haversine formula
        R = 6371  # Earth radius in km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_lat/2) * math.sin(delta_lat/2) +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lng/2) * math.sin(delta_lng/2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def find_nearest_hospitals(self, user_lat, user_lng, ayushman_only=False, max_distance_km=50):
        """Find nearest hospitals with filters"""
        eligible_hospitals = []
        
        for hospital in self.hospitals:
            # Calculate distance
            distance = self.calculate_distance(
                user_lat, user_lng,
                hospital['lat'], hospital['lng']
            )
            
            # Apply distance filter
            if distance > max_distance_km:
                continue
            
            # Apply Ayushman filter
            if ayushman_only and not hospital.get('ayushman', False):
                continue
            
            # Add distance to hospital data
            hospital_with_distance = hospital.copy()
            hospital_with_distance['distance_km'] = round(distance, 1)
            hospital_with_distance['travel_time_min'] = round(distance * 2)  # Rough estimate
            
            # Add Ayushman details if available
            if hospital.get('ayushman', False):
                ayushman_info = self.get_ayushman_info(hospital['id'])
                hospital_with_distance['ayushman_details'] = ayushman_info
            
            eligible_hospitals.append(hospital_with_distance)
        
        # Sort by distance
        eligible_hospitals.sort(key=lambda x: x['distance_km'])
        
        return eligible_hospitals[:10]  # Return top 10 nearest
    
    def get_ayushman_info(self, hospital_id):
        """Get Ayushman Bharat details for hospital"""
        for empaneled in self.ayushman_data.get('ayushman_empaneled', []):
            if empaneled['hospital_id'] == hospital_id:
                return empaneled
        return None
    
    def find_hospitals_by_specialty(self, specialty, user_lat, user_lng, ayushman_only=False):
        """Find hospitals by medical specialty"""
        all_hospitals = self.find_nearest_hospitals(user_lat, user_lng, ayushman_only)
        
        specialty_hospitals = []
        for hospital in all_hospitals:
            if specialty.lower() in [s.lower() for s in hospital.get('specialties', [])]:
                specialty_hospitals.append(hospital)
        
        return specialty_hospitals
    
    def get_emergency_contacts(self, hospital_id):
        """Get emergency contact information"""
        for hospital in self.hospitals:
            if hospital['id'] == hospital_id:
                return {
                    'emergency_phone': hospital.get('phone'),
                    'ambulance_phone': hospital.get('ambulance_contact', hospital.get('phone')),
                    'emergency_services': hospital.get('emergency_services', False)
                }
        return None

# Global instance
hospital_finder = HospitalFinder()

# Updated find_nearest_hospitals function
def find_nearest_hospitals(user_lat, user_lng, ayushman_only=False):
    return hospital_finder.find_nearest_hospitals(user_lat, user_lng, ayushman_only)
