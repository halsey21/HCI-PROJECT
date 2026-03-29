from django.contrib import admin
from .models import Report, CommunityFeed

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('reference_number', 'issue_type', 'status', 'created_at')
    list_filter = ('status', 'issue_type')
    search_fields = ('reference_number', 'location', 'description')
    readonly_fields = ('reference_number', 'created_at', 'updated_at')

@admin.register(CommunityFeed)
class CommunityFeedAdmin(admin.ModelAdmin):
    list_display = ('report', 'message', 'created_at')
