from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('submit/', views.submit_website, name='submit_website'),
    path('success/', views.success, name='success'),
    path('website/<slug:slug>/', views.website_detail, name='website_detail'),
    
    # Rating, Review, Report (require login)
    path('website/<slug:slug>/rate/', views.rate_website, name='rate_website'),
    path('website/<slug:slug>/review/', views.review_website, name='review_website'),
    path('website/<slug:slug>/report/', views.report_website, name='report_website'),
    
    # Admin
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('approve/<int:pk>/', views.approve_website, name='approve_website'),
    path('reject/<int:pk>/', views.reject_website, name='reject_website'),
    path('resolve-report/<int:pk>/', views.resolve_report, name='resolve_report'),
]
