from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
from .models import User, PatientProfile, TriageSession, MedicationReminder

@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            user = User.objects.create_user(
                username=data['email'],
                email=data['email'],
                password=data['password'],
                first_name=data.get('name', ''),
                phone_number=data.get('phone', '')
            )
            PatientProfile.objects.create(user=user)
            return JsonResponse({'success': True, 'message': 'User created successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user = authenticate(username=data['email'], password=data['password'])
        if user:
            login(request, user)
            return JsonResponse({'success': True, 'user': {'name': user.first_name, 'email': user.email}})
        return JsonResponse({'success': False, 'error': 'Invalid credentials'})

@login_required
def get_user_dashboard(request):
    triage_sessions = TriageSession.objects.filter(patient=request.user).order_by('-created_at')[:10]
    reminders = MedicationReminder.objects.filter(patient=request.user, is_active=True)
    
    data = {
        'user': {
            'name': request.user.first_name,
            'email': request.user.email,
            'phone': request.user.phone_number
        },
        'triage_history': [
            {
                'symptoms': session.symptoms[:100] + '...' if len(session.symptoms) > 100 else session.symptoms,
                'severity': session.severity,
                'date': session.created_at.strftime('%Y-%m-%d %H:%M'),
                'session_id': session.session_id
            }
            for session in triage_sessions
        ],
        'active_reminders': [
            {
                'medicine_name': reminder.medicine_name,
                'dosage': reminder.dosage,
                'time': reminder.reminder_time.strftime('%H:%M'),
                'frequency': reminder.get_frequency_display()
            }
            for reminder in reminders
        ]
    }
    return JsonResponse(data)

@csrf_exempt
@login_required
def set_medication_reminder(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        reminder = MedicationReminder.objects.create(
            patient=request.user,
            medicine_name=data['medicine_name'],
            dosage=data['dosage'],
            frequency=data['frequency'],
            reminder_time=data['reminder_time']
        )
        return JsonResponse({'success': True, 'reminder_id': reminder.id})