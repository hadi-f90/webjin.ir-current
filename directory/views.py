from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Avg
from .models import Website, Category, Tag, Rating, Review, Report
from .forms import WebsiteSubmitForm, RatingForm, ReviewForm, ReportForm


def is_admin(user):
    return user.is_staff


def index(request):
    websites = Website.objects.filter(status='approved')
    categories = Category.objects.all()
    
    # Filter by category
    category_slug = request.GET.get('category')
    if category_slug:
        websites = websites.filter(category__slug=category_slug)
    
    # Filter by tag
    tag_slug = request.GET.get('tag')
    if tag_slug:
        websites = websites.filter(tags__slug=tag_slug)
    
    # Search
    search = request.GET.get('search')
    if search:
        websites = websites.filter(title__icontains=search) | websites.filter(description__icontains=search)
    
    # Pagination
    paginator = Paginator(websites, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': category_slug,
    }
    return render(request, 'directory/index.html', context)


def website_detail(request, slug):
    website = get_object_or_404(Website, slug=slug, status='approved')
    related_websites = Website.objects.filter(
        category=website.category, 
        status='approved'
    ).exclude(id=website.id)[:4]
    
    # Get approved reviews
    reviews = website.reviews.filter(is_approved=True)[:10]
    
    # User's rating (if logged in)
    user_rating = None
    user_review = None
    user_report = None
    
    if request.user.is_authenticated:
        user_rating = website.ratings.filter(user=request.user).first()
        user_review = website.reviews.filter(user=request.user).first()
        user_report = website.reports.filter(user=request.user).first()
    
    # Forms
    rating_form = RatingForm()
    review_form = ReviewForm()
    report_form = ReportForm()
    
    context = {
        'website': website,
        'related_websites': related_websites,
        'reviews': reviews,
        'rating_form': rating_form,
        'review_form': review_form,
        'report_form': report_form,
        'user_rating': user_rating,
        'user_review': user_review,
        'user_report': user_report,
    }
    return render(request, 'directory/detail.html', context)


@login_required
def rate_website(request, slug):
    """Rate a website - requires login"""
    website = get_object_or_404(Website, slug=slug, status='approved')
    
    if request.method == 'POST':
        rating_value = request.POST.get('rating')
        if rating_value:
            # Check if user already rated
            rating, created = Rating.objects.update_or_create(
                website=website,
                user=request.user,
                defaults={'rating': int(rating_value)}
            )
            website.update_rating()
            messages.success(request, 'امتیاز شما ثبت شد!')
    
    return redirect('website_detail', slug=slug)


@login_required
def review_website(request, slug):
    """Review a website - requires login"""
    website = get_object_or_404(Website, slug=slug, status='approved')
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            # Check if user already reviewed
            review, created = Review.objects.update_or_create(
                website=website,
                user=request.user,
                defaults={
                    'content': form.cleaned_data['content'],
                    'is_approved': True  # Auto-approve for now
                }
            )
            messages.success(request, 'نظر شما ثبت شد!')
    
    return redirect('website_detail', slug=slug)


@login_required
def report_website(request, slug):
    """Report a website - requires login"""
    website = get_object_or_404(Website, slug=slug, status='approved')
    
    # Check if user already reported
    existing_report = website.reports.filter(user=request.user).exists()
    
    if existing_report:
        messages.warning(request, 'شما قبلاً این وب‌سایت را گزارش کرده‌اید.')
        return redirect('website_detail', slug=slug)
    
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            Report.objects.create(
                website=website,
                user=request.user,
                report_type=form.cleaned_data['report_type'],
                description=form.cleaned_data.get('description', '')
            )
            messages.success(request, 'گزارش شما ثبت شد. متشکریم!')
    
    return redirect('website_detail', slug=slug)


def submit_website(request):
    if request.method == 'POST':
        form = WebsiteSubmitForm(request.POST)
        if form.is_valid():
            website = form.save(commit=False)
            website.status = 'pending'
            if request.user.is_authenticated:
                website.created_by = request.user
            website.save()
            messages.success(request, 'وب‌سایت شما با موفقیت ثبت شد!')
            return redirect('success')
    else:
        form = WebsiteSubmitForm()
    
    categories = Category.objects.all()
    return render(request, 'directory/submit.html', {
        'form': form, 
        'categories': categories
    })


def success(request):
    return render(request, 'directory/success.html')


@user_passes_test(is_admin)
def admin_dashboard(request):
    pending_websites = Website.objects.filter(status='pending')
    approved_websites = Website.objects.filter(status='approved')
    rejected_websites = Website.objects.filter(status='rejected')
    reports = Report.objects.filter(is_resolved=False)
    
    context = {
        'pending': pending_websites,
        'approved': approved_websites,
        'rejected': rejected_websites,
        'reports': reports,
    }
    return render(request, 'directory/admin_dashboard.html', context)


@user_passes_test(is_admin)
def approve_website(request, pk):
    website = get_object_or_404(Website, pk=pk)
    website.status = 'approved'
    website.save()
    messages.success(request, f'{website.title} تأیید شد!')
    return redirect('admin_dashboard')


@user_passes_test(is_admin)
def reject_website(request, pk):
    website = get_object_or_404(Website, pk=pk)
    website.status = 'rejected'
    website.save()
    messages.warning(request, f'{website.title} رد شد.')
    return redirect('admin_dashboard')


@user_passes_test(is_admin)
def resolve_report(request, pk):
    report = get_object_or_404(Report, pk=pk)
    report.is_resolved = True
    report.save()
    messages.success(request, 'گزارش حل شد.')
    return redirect('admin_dashboard')
