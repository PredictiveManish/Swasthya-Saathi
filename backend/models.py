from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    emergency_contact = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    blood_group = models.CharField(max_length=5, blank=True)
    allergies = models.TextField(blank=True)
    medical_history = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

class TriageSession(models.Model):
    SEVERITY_CHOICES = [
        ('Emergency', 'Emergency'),
        ('OPD Visit', 'OPD Visit'),
        ('Self-care', 'Self-care'),
    ]
    
    patient = models.ForeignKey(User, on_delete=models.CASCADE)
    symptoms = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    advice = models.TextField()
    reasoning = models.TextField()
    session_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(default=timezone.now)

class MedicationReminder(models.Model):
    FREQUENCY_CHOICES = [
        ('once_daily', 'Once Daily'),
        ('twice_daily', 'Twice Daily'),
        ('thrice_daily', 'Thrice Daily'),
        ('weekly', 'Weekly'),
    ]
    
    patient = models.ForeignKey(User, on_delete=models.CASCADE)
    medicine_name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=50)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    reminder_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

class DoctorConsultation(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE)
    doctor_name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100)
    consultation_type = models.CharField(max_length=50)  # video, voice, chat
    status = models.CharField(max_length=20, default='scheduled')
    scheduled_time = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)