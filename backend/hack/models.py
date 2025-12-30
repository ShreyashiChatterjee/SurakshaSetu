from django.db import models
from django.contrib.auth.models import User

class EmergencyContact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.phone}"

    class Meta:
        ordering = ['-created_at']


class IncidentReport(models.Model):
    INCIDENT_TYPES = [
        ('harassment', 'Harassment'),
        ('stalking', 'Stalking'),
        ('assault', 'Physical Assault'),
        ('domestic-violence', 'Domestic Violence'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('under-investigation', 'Under Investigation'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='incident_reports')
    incident_type = models.CharField(max_length=20, choices=INCIDENT_TYPES)
    location = models.CharField(max_length=255)
    description = models.TextField()
    is_anonymous = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.incident_type} - {self.location} ({self.status})"

    class Meta:
        ordering = ['-created_at']


class SOSAlert(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='sos_alerts')
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        user_info = self.user.username if self.user else "Anonymous"
        return f"SOS Alert from {user_info} at ({self.latitude}, {self.longitude})"

    class Meta:
        ordering = ['-created_at']