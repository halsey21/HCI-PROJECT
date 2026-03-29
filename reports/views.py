from django.shortcuts import render, redirect, get_object_or_404
from .models import Report, CommunityFeed, Notification, Support, Verification
from .forms import ReportForm
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse
import json

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to Track My Waste, {user.username}!")
            return redirect('menu')
    else:
        form = UserCreationForm()
    return render(request, 'reports/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('menu')
    else:
        form = AuthenticationForm()
    return render(request, 'reports/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('menu')

def report_list(request):
    # Public reports that anyone can see
    category = request.GET.get('category')
    community_reports = Report.objects.filter(is_public=True).order_by('-created_at')
    
    if category and category != 'ALL':
        community_reports = community_reports.filter(issue_type=category)
    
    # User's own reports (private and public)
    my_reports = []
    if request.user.is_authenticated:
        my_reports = Report.objects.filter(user=request.user).order_by('-created_at')
    
    resolved_count = Report.objects.filter(status__in=['RESOLVED', 'VERIFIED']).count()
    alerts_count = Notification.objects.filter(is_sms=True).count() or 1
    
    community_info = {
        'similar_nearby': 3,
        'residents_tracking': 8
    }
    return render(request, 'reports/report_list.html', {
        'community_reports': community_reports,
        'my_reports': my_reports,
        'resolved_count': resolved_count,
        'alerts_count': alerts_count,
        'community_info': community_info,
        'selected_category': category or 'ALL'
    })

@login_required
def create_report(request):
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.user = request.user
            # In a real app, we'd get coordinates from a map or GPS
            # For this simulation, they are generated in the model's save() method
            report.save()
            
            # Create notification
            Notification.objects.create(
                title='Report Received',
                message=f'Your report #{report.reference_number} for {report.get_issue_type_display()} has been received.',
                report=report,
                icon='fas fa-file-alt',
                color='text-blue'
            )
            
            # If SMS preference, create an SMS notification too
            if report.contact_preference == 'SMS':
                Notification.objects.create(
                    title='SMS Alert',
                    message=f'CITY OF JOBURG: Your report {report.reference_number} is logged. Track at bit.ly/track-joburg',
                    report=report,
                    is_sms=True,
                    icon='fas fa-comment-sms',
                    color='text-yellow'
                )
                
            messages.success(request, f"Report submitted successfully! Reference: {report.reference_number}")
            return redirect('report_list')
    else:
        form = ReportForm()
    return render(request, 'reports/report_form.html', {'form': form})

def report_detail(request, reference_number):
    report = get_object_or_404(Report, reference_number=reference_number)
    supports_count = report.supports.count()
    user_supported = False
    if request.user.is_authenticated:
        user_supported = report.supports.filter(user=request.user).exists()
        
    return render(request, 'reports/report_detail.html', {
        'report': report,
        'supports_count': supports_count,
        'user_supported': user_supported
    })

@login_required
@require_POST
def verify_resolution(request, reference_number):
    report = get_object_or_404(Report, reference_number=reference_number)
    status = request.POST.get('status') # 'CONFIRM' or 'DISPUTE'
    comments = request.POST.get('comments', '')
    
    if report.status == 'RESOLVED':
        Verification.objects.update_or_create(
            report=report,
            defaults={'status': status, 'comments': comments}
        )
        
        if status == 'CONFIRM':
            report.status = 'VERIFIED'
            report.save()
            Notification.objects.create(
                title='Issue Verified',
                message=f'You have verified the resolution of #{report.reference_number}. Thank you!',
                report=report,
                icon='fas fa-check-double',
                color='text-green'
            )
        else:
            # If disputed, we might want to set it back to IN_PROGRESS or a special state
            report.status = 'IN_PROGRESS'
            report.save()
            Notification.objects.create(
                title='Resolution Disputed',
                message=f'The resolution of #{report.reference_number} has been disputed and reopened.',
                report=report,
                icon='fas fa-exclamation-triangle',
                color='text-red'
            )
            
        messages.success(request, f"Your feedback for {report.reference_number} has been recorded.")
        
    return redirect('report_detail', reference_number=reference_number)

@login_required
@require_POST
def add_support(request, reference_number):
    report = get_object_or_404(Report, reference_number=reference_number)
    support, created = Support.objects.get_or_create(report=report, user=request.user)
    
    if created:
        messages.success(request, f"You added your support to report {report.reference_number}.")
    else:
        support.delete()
        messages.info(request, f"You removed your support from report {report.reference_number}.")
        
    return redirect('report_detail', reference_number=reference_number)

@require_GET
def track_search(request):
    ref_num = request.GET.get('ref_num')
    if ref_num:
        report = Report.objects.filter(reference_number=ref_num).first()
        if report:
            return redirect('report_detail', reference_number=report.reference_number)
        else:
            messages.error(request, f"No report found with ID: {ref_num}")
    return redirect('menu')

@require_POST
def track_report(request, reference_number):
    report = get_object_or_404(Report, reference_number=reference_number)
    report.tracking_count += 1
    report.save()
    return redirect('report_detail', reference_number=reference_number)

def menu_view(request):
    return render(request, 'reports/menu.html')

def notifications_view(request):
    notifications = Notification.objects.all().order_by('-created_at')
    
    # If no real notifications, show some simulated ones
    if not notifications.exists():
        notifications = [
            {'title': 'Status Update', 'message': 'Your report #JOBURG-2403 has been assigned to a crew.', 'time': '2 hours ago', 'icon': 'fas fa-info-circle', 'color': 'text-blue'},
            {'title': 'Resolution Confirmation', 'message': 'Report #JOBURG-2401 is resolved. Please verify.', 'time': '5 hours ago', 'icon': 'fas fa-check-circle', 'color': 'text-green'},
        ]
        
    return render(request, 'reports/notifications.html', {'notifications': notifications})

def about_view(request):
    return render(request, 'reports/about.html')

def community_map_view(request):
    # Fetch actual reports with coordinates
    reports = Report.objects.filter(latitude__isnull=False, longitude__isnull=False)
    
    markers = []
    for r in reports:
        markers.append({
            'lat': float(r.latitude),
            'lng': float(r.longitude),
            'title': f'Report #{r.reference_number}',
            'description': f'{r.get_issue_type_display()} at {r.location}'
        })
        
    # If no reports, add some defaults in Johannesburg
    if not markers:
        markers = [
            {'lat': -26.2041, 'lng': 28.0473, 'title': 'Soweto (Orlando West)', 'description': '3 active reports nearby'},
            {'lat': -26.1450, 'lng': 28.0339, 'title': 'Rosebank', 'description': '1 report in progress'},
            {'lat': -26.1076, 'lng': 28.0567, 'title': 'Sandton', 'description': '2 active reports'},
        ]
        
    return render(request, 'reports/community_map.html', {'markers': markers})

def schedule_view(request):
    schedule_data = [
        {'area': 'Soweto (Orlando West)', 'day': 'Friday', 'time': '07:00', 'notes': 'Early morning collection'},
        {'area': 'Rosebank', 'day': 'Monday', 'time': '08:00', 'notes': 'Standard domestic waste collection'},
        {'area': 'Sandton', 'day': 'Thursday', 'time': '08:15', 'notes': 'Standard domestic waste'},
        {'area': 'Randburg', 'day': 'Tuesday', 'time': '07:30', 'notes': 'Garden waste and domestic bins'},
        {'area': 'Midrand', 'day': 'Wednesday', 'time': '09:00', 'notes': 'Recycling and standard collection'},
    ]
    return render(request, 'reports/schedule.html', {'schedule_data': schedule_data})
