# Add these imports at the top
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.http import JsonResponse
from django.db.models import Q, Count
from .models import Website, Category, Tag, Rating, Review, Report
from .forms import WebsiteSubmitForm, RatingForm, ReviewForm, ReportForm
import random


def is_admin(user):
    return user.is_staff


# ==================== Home Page ====================

def index(request):
    websites = Website.objects.filter(status='approved')
    categories = Category.objects.annotate(website_count=Count('website_set'))
    all_tags = Tag.objects.annotate(website_count=Count('websites')).order_by('-website_count')[:10]
    
    category_slug = request.GET.get('category')
    if category_slug:
        websites = websites.filter(category__slug=category_slug)
    
    tag_slug = request.GET.get('tag')
    if tag_slug:
        websites = websites.filter(tags__slug=tag_slug)
    
    search = request.GET.get('search')
    if search:
        websites = websites.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search) |
            Q(tags__name__icontains=search)
        ).distinct()
    
    featured_websites = list(Website.objects.filter(status='approved'))
    random.shuffle(featured_websites)
    featured_websites = featured_websites[:6]
    
    paginator = Paginator(websites, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'all_tags': all_tags,
        'featured_websites': featured_websites,
        'selected_category': category_slug,
    }
    return render(request, 'directory/index.html', context)


def search_suggestions(request):
    query = request.GET.get('q', '')
    
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    websites = Website.objects.filter(
        status='approved',
        title__icontains=query
    )[:5]
    
    tags = Tag.objects.filter(name__icontains=query)[:5]
    
    suggestions = []
    
    for w in websites:
        suggestions.append({
            'type': 'website',
            'title': w.title,
            'url': w.get_absolute_url(),
            'icon': 'bi-globe'
        })
    
    for t in tags:
        suggestions.append({
            'type': 'tag',
            'title': t.name,
            'url': f'?tag={t.slug}',
            'icon': 'bi-tag'
        })
    
    return JsonResponse({'suggestions': suggestions[:10]})


def website_detail(request, slug):
    website = get_object_or_404(Website, slug=slug, status='approved')
    related_websites = Website.objects.filter(
        category=website.category, 
        status='approved'
    ).exclude(id=website.id)[:4]
    
    reviews = website.reviews.filter(is_approved=True)[:10]
    
    user_rating = None
    user_review = None
    user_report = None
    is_owner = False
    
    if request.user.is_authenticated:
        user_rating = website.ratings.filter(user=request.user).first()
        user_review = website.reviews.filter(user=request.user).first()
        user_report = website.reports.filter(user=request.user).first()
        is_owner = website.created_by == request.user
    
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
        'is_owner': is_owner,
    }
    return render(request, 'directory/detail.html', context)


# ==================== Rating, Review, Report ====================

@login_required
def rate_website(request, slug):
    website = get_object_or_404(Website, slug=slug, status='approved')
    
    if request.method == 'POST':
        rating_value = request.POST.get('rating')
        if rating_value:
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
    website = get_object_or_404(Website, slug=slug, status='approved')
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review, created = Review.objects.update_or_create(
                website=website,
                user=request.user,
                defaults={
                    'content': form.cleaned_data['content'],
                    'is_approved': True
                }
            )
            messages.success(request, 'نظر شما ثبت شد!')
    
    return redirect('website_detail', slug=slug)


@login_required
def report_website(request, slug):
    website = get_object_or_404(Website, slug=slug, status='approved')
    
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


# ==================== Submit Website ====================

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


# ==================== Edit Website ====================

@login_required
def edit_website(request, slug):
    website = get_object_or_404(Website, slug=slug)
    
    # Only owner or admin can edit
    if website.created_by != request.user and not request.user.is_staff:
        messages.error(request, 'شما اجازه ویرایش این وب‌سایت را ندارید.')
        return redirect('website_detail', slug=slug)
    
    if request.method == 'POST':
        form = WebsiteSubmitForm(request.POST, instance=website)
        if form.is_valid():
            website = form.save(commit=False)
            # Reset status to pending for re-approval if significant changes
            website.status = 'pending'
            website.save()
            messages.success(request, 'وب‌سایت با موفقیت ویرایش شد!')
            return redirect('website_detail', slug=website.slug)
    else:
        form = WebsiteSubmitForm(instance=website)
    
    categories = Category.objects.all()
    # Pre-fill tags
    current_tags = ', '.join([tag.name for tag in website.tags.all()])
    
    return render(request, 'directory/edit_website.html', {
        'form': form,
        'categories': categories,
        'website': website,
        'current_tags': current_tags
    })


def success(request):
    return render(request, 'directory/success.html')


# ==================== Auth ====================

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'حساب کاربری شما ایجاد شد!')
            return redirect('index')
    else:
        form = UserCreationForm()
    
    return render(request, 'directory/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'خوش آمدید!')
                return redirect('index')
    else:
        form = AuthenticationForm()
    
    return render(request, 'directory/login.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.info(request, 'از حساب خود خارج شدید.')
    return redirect('index')


# ==================== User Dashboard ====================

@login_required
def user_dashboard(request):
    my_websites = Website.objects.filter(created_by=request.user)
    my_ratings = Rating.objects.filter(user=request.user)
    my_reviews = Review.objects.filter(user=request.user)
    
    context = {
        'my_websites': my_websites,
        'my_ratings': my_ratings,
        'my_reviews': my_reviews,
    }
    return render(request, 'directory/user_dashboard.html', context)


@login_required
def delete_my_website(request, pk):
    website = get_object_or_404(Website, pk=pk, created_by=request.user)
    website.delete()
    messages.success(request, 'وب‌سایت حذف شد.')
    return redirect('user_dashboard')


@login_required
def delete_my_review(request, pk):
    review = get_object_or_404(Review, pk=pk, user=request.user)
    review.delete()
    messages.success(request, 'نظر حذف شد.')
    return redirect('user_dashboard')


# ==================== Static Pages ====================

def about(request):
    return render(request, 'directory/about.html')


def terms(request):
    return render(request, 'directory/terms.html')


# ==================== Admin Dashboard ====================

@user_passes_test(is_admin)
def admin_dashboard(request):
    pending_websites = Website.objects.filter(status='pending')
    approved_websites = Website.objects.filter(status='approved')
    rejected_websites = Website.objects.filter(status='rejected')
    reports = Report.objects.filter(is_resolved=False)
    categories = Category.objects.all()
    tags = Tag.objects.all()
    
    context = {
        'pending': pending_websites,
        'approved': approved_websites,
        'rejected': rejected_websites,
        'reports': reports,
        'categories': categories,
        'tags': tags,
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


@user_passes_test(is_admin)
def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        icon = request.POST.get('icon', 'bi-folder')
        if name:
            Category.objects.create(name=name, description=description, icon=icon)
            messages.success(request, 'دسته‌بندی اضافه شد!')
    return redirect('admin_dashboard')


@user_passes_test(is_admin)
def add_tag(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Tag.objects.get_or_create(name=name)
            messages.success(request, 'برچسب اضافه شد!')
    return redirect('admin_dashboard')
