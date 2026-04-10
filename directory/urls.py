from django.urls import path
from . import views
from django.http import JsonResponse
from .forms import tag_suggestions

urlpatterns = [
    # Home
    path('', views.index, name='index'),
    path('search/suggestions/', views.search_suggestions, name='search_suggestions'),

    # Auth
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),

    # Website
    path('submit/', views.submit_website, name='submit_website'),
    path('success/', views.success, name='success'),
    path('website/<slug:slug>/', views.website_detail, name='website_detail'),
    path('website/<slug:slug>/edit/', views.edit_website, name='edit_website'),

    # Actions
    path('website/<slug:slug>/rate/', views.rate_website, name='rate_website'),
    path('website/<slug:slug>/review/', views.review_website, name='review_website'),
    path('website/<slug:slug>/report/', views.report_website, name='report_website'),

    # User actions
    path('website/delete/<int:pk>/', views.delete_my_website, name='delete_my_website'),
    path('review/delete/<int:pk>/', views.delete_my_review, name='delete_my_review'),

    # Static pages
    path('about/', views.about, name='about'),
    path('terms/', views.terms, name='terms'),

    # Admin
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('approve/<int:pk>/', views.approve_website_ajax, name='approve_website'),
    path('ajax/reject/<int:pk>/', views.reject_website_ajax, name='reject_website_ajax'),
    path('ajax/delete/<int:pk>/', views.delete_website_ajax, name='delete_website_ajax'),
    path(
        'ajax/update-status/<int:pk>/',
        views.update_website_status_ajax,
        name='update_website_status_ajax',
    ),
    path('ajax/edit-website/<int:pk>/', views.edit_website_ajax, name='edit_website_ajax'),
    path('resolve-report/<int:pk>/', views.resolve_report_ajax, name='resolve_report_ajax'),
    # Category AJAX URLs
    path('ajax/add-category/', views.add_category_ajax, name='add_category_ajax'),
    path('ajax/edit-category/<int:pk>/', views.edit_category_ajax, name='edit_category_ajax'),
    path('ajax/delete-category/<int:pk>/', views.delete_category_ajax, name='delete_category_ajax'),
        # Tag AJAX URLs
    path('ajax/add-tag/', views.add_tag_ajax, name='add_tag_ajax'),     # Note: This redirects, maybe make it AJAX too? For now keeping as is.
    path('ajax/edit-tag/<int:pk>/', views.edit_tag_ajax, name='edit_tag_ajax'),
    path('ajax/delete-tag/<int:pk>/', views.delete_tag_ajax, name='delete_tag_ajax'),
    path('add-tag/', views.add_tag_ajax, name='add_tag'),
    path('tags/suggestions/', tag_suggestions, name='tag_suggestions'),

    # Category & Tag Pages (SEO-friendly)
    # path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    # path('tag/<slug:slug>/', views.tag_detail, name='tag_detail'),
]
