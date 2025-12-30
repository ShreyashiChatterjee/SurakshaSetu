from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # ============================================
    # ADMIN PANEL
    # ============================================
    #path('admin/', admin.site.urls),
    
    # ============================================
    # PAGE ROUTES - Serve HTML Templates
    # ============================================
    path('', views.login_view, name='login'),
    path('home/', views.home_view, name='home'),
    path('my-cases/', views.my_cases_view, name='my_cases'),
    
    # ============================================
    # API ROUTES - AJAX Endpoints
    # ============================================
    path('api/login/', views.login_api, name='login_api'),
    path('api/sos/', views.sos_api, name='sos_api'),
    path('api/save-case/', views.save_case, name='save_case'),
    path('api/get-cases/', views.get_cases, name='get_cases'),
    path('api/cases/<int:case_id>/', views.delete_case, name='delete_case'),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)