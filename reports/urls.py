from django.urls import path
from . import views

urlpatterns = [
    path('', views.menu_view, name='menu'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('reports/', views.report_list, name='report_list'),
    path('report/new/', views.create_report, name='create_report'),
    path('report/<str:reference_number>/', views.report_detail, name='report_detail'),
    path('report/<str:reference_number>/verify/', views.verify_resolution, name='verify_resolution'),
    path('report/<str:reference_number>/support/', views.add_support, name='add_support'),
    path('track/search/', views.track_search, name='track_search'),
    path('report/<str:reference_number>/track/', views.track_report, name='track_report'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('about/', views.about_view, name='about'),
    path('schedule/', views.schedule_view, name='schedule'),
    path('map/', views.community_map_view, name='community_map'),
]
