from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('submit/', views.submit_website, name='submit_website'),
    path('success/', views.success, name='success'),
    path('website/<slug:slug>/', views.website_detail, name='website_detail'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('approve/<int:pk>/', views.approve_website, name='approve_website'),
    path('reject/<int:pk>/', views.reject_website, name='reject_website'),
]