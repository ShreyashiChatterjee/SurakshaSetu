from django.contrib import admin
from .models import EmergencyContact, IncidentReport, SOSAlert


@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'phone', 'user__username')
    ordering = ('-created_at',)


@admin.register(IncidentReport)
class IncidentReportAdmin(admin.ModelAdmin):
    list_display = ('incident_type', 'location', 'status', 'is_anonymous', 'user', 'created_at')
    list_filter = ('incident_type', 'status', 'is_anonymous', 'created_at')
    search_fields = ('location', 'description', 'user__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Report Information', {
            'fields': ('user', 'incident_type', 'location', 'description', 'is_anonymous')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SOSAlert)
class SOSAlertAdmin(admin.ModelAdmin):
    list_display = ('user', 'latitude', 'longitude', 'is_resolved', 'created_at')
    list_filter = ('is_resolved', 'created_at')
    search_fields = ('user__username',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Alert Information', {
            'fields': ('user', 'latitude', 'longitude', 'is_resolved')
        }),
        ('Timestamp', {
            'fields': ('created_at',),
        }),
    )