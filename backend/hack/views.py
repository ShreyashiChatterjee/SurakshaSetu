from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import IncidentReport, EmergencyContact, SOSAlert


# ============================================
# PAGE VIEWS - Render HTML Templates
# ============================================

def login_view(request):
    """Render the login page"""
    return render(request, 'login.html')


def home_view(request):
    """Render the home/dashboard page"""
    return render(request, 'index.html')


def my_cases_view(request):
    """Render the my cases page"""
    return render(request, 'mycases.html')


# ============================================
# API VIEWS - Handle AJAX Requests
# ============================================

@csrf_exempt
@require_http_methods(["POST"])
def login_api(request):
    """
    Handle user login/registration
    Expected JSON: { "phone": "1234567890", "name": "John Doe", "contacts": [...] }
    """
    try:
        data = json.loads(request.body)
        phone = data.get('phone')
        name = data.get('name')
        contacts = data.get('contacts', [])

        # Validate required fields
        if not phone or not name:
            return JsonResponse({
                'status': 'error',
                'message': 'Phone and name are required'
            }, status=400)

        # Get or create user by phone number
        user, created = User.objects.get_or_create(username=phone)
        
        # Update user info
        user.first_name = name
        user.save()

        # Clear old contacts and add new ones
        EmergencyContact.objects.filter(user=user).delete()
        
        for contact in contacts:
            if contact.get('name') and contact.get('phone'):
                EmergencyContact.objects.create(
                    user=user,
                    name=contact['name'],
                    phone=contact['phone']
                )

        # Log the user in
        login(request, user)

        return JsonResponse({
            'status': 'success',
            'user_id': user.id,
            'message': 'Login successful'
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def sos_api(request):
    """
    Handle SOS emergency alerts
    Expected JSON: { "latitude": 12.34, "longitude": 56.78, "user_id": 1 }
    """
    try:
        data = json.loads(request.body)
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        user_id = data.get('user_id')

        # Validate coordinates
        if latitude is None or longitude is None:
            return JsonResponse({
                'status': 'error',
                'message': 'Latitude and longitude are required'
            }, status=400)

        # Get user if authenticated
        user = None
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                pass

        # Create SOS alert
        sos_alert = SOSAlert.objects.create(
            user=user,
            latitude=latitude,
            longitude=longitude
        )

        return JsonResponse({
            'status': 'success',
            'message': 'Emergency alert sent successfully!',
            'alert_id': sos_alert.id
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def save_case(request):
    """
    Save a new incident report
    Expected JSON: { 
        "incident_type": "harassment", 
        "location": "...", 
        "description": "...", 
        "is_anonymous": false,
        "user_id": 1 
    }
    """
    try:
        data = json.loads(request.body)
        incident_type = data.get('incident_type')
        location = data.get('location')
        description = data.get('description')
        is_anonymous = data.get('is_anonymous', False)
        user_id = data.get('user_id')  # ✅ Added

        # Validate required fields
        if not incident_type or not location or not description:
            return JsonResponse({
                'status': 'error',
                'message': 'Incident type, location, and description are required'
            }, status=400)

        # ✅ Try to get user from user_id (sent from frontend)
        user = None
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                pass

        # ✅ Fallback for authenticated session (optional)
        if not user and request.user.is_authenticated:
            user = request.user

        # ✅ Final check
        if not user:
            return JsonResponse({
                'status': 'error',
                'message': 'No user found. Please login first.'
            }, status=401)

        # ✅ Create incident report
        new_report = IncidentReport.objects.create(
            user=user,
            incident_type=incident_type,
            location=location,
            description=description,
            is_anonymous=is_anonymous,
            status='pending'  # Default status
        )

        return JsonResponse({
            'status': 'success',
            'case_id': new_report.id,
            'message': 'Case reported successfully'
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        }, status=500)



@require_http_methods(["GET"])
def get_cases(request):
    """
    Get all incident reports
    Returns JSON array of all cases
    """
    try:
        # Get all reports ordered by most recent first
        reports = IncidentReport.objects.all().order_by('-created_at')
        
        # Serialize the data
        data = []
        for report in reports:
            data.append({
                'id': report.id,
                'incident_type': report.incident_type,
                'location': report.location,
                'description': report.description,
                'status': report.status,
                'is_anonymous': report.is_anonymous,
                'created_at': report.created_at.isoformat(),
                'date': report.created_at.strftime("%b %d, %Y at %I:%M %p")
            })

        return JsonResponse(data, safe=False)

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_case(request, case_id):
    """
    Delete an incident report by ID
    URL: /api/cases/<case_id>/
    """
    try:
        # Find and delete the report
        report = IncidentReport.objects.get(id=case_id)
        report.delete()

        return JsonResponse({
            'status': 'success',
            'message': 'Case deleted successfully'
        })

    except IncidentReport.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Case not found'
        }, status=404)
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        }, status=500)