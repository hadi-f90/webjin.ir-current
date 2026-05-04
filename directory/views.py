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
from django_ratelimit.decorators import ratelimit
import json
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
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
    is_owner = (website.created_by == request.user) or request.user.is_staff
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
@ratelimit(key='user', rate='5/m')
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
            messages.success(request, 'وب‌سایت با موفقیت ویرایش شد و در انتظار تأیید مجدد است.')
            return redirect('user_dashboard')  # Redirect to dashboard instead of detail
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
    # We use select_related to optimize queries
    pending_websites = Website.objects.select_related('category').filter(status='pending')
    approved_websites = Website.objects.select_related('category').filter(status='approved')
    rejected_websites = Website.objects.select_related('category').filter(status='rejected')
    reports = Report.objects.select_related('website', 'user').filter(is_resolved=False)

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


@require_POST
@staff_member_required
def approve_website_ajax(request, pk):
    website = get_object_or_404(Website, pk=pk)
    website.status = 'approved'
    website.save()
    return JsonResponse(
        {'status': 'success', 'message': f"{website.title} تأیید شد!", "new_status": "approved"}
    )


@require_POST
@staff_member_required
def reject_website_ajax(request, pk):
    website = get_object_or_404(Website, pk=pk)
    website.status = 'rejected'
    website.save()
    return JsonResponse({
        'status': 'success',
        'message': f'{website.title} رد شد.',
        'new_status': 'rejected'
    })

@require_POST
@staff_member_required
def delete_website_ajax(request, pk):
    website = get_object_or_404(Website, pk=pk)
    website_title = website.title
    website.delete()
    return JsonResponse(
        {'status': 'success', 'message': f"{website_title} حذف شد.", "deleted": True}
    )


@require_POST
@staff_member_required
def update_website_status_ajax(request, pk):
    """Handles changing status from Approved to Rejected via dropdown"""
    website = get_object_or_404(Website, pk=pk)
    new_status = request.POST.get('status')

    if new_status in {'pending', 'approved', 'rejected'}:
        website.status = new_status
        website.save()
        return JsonResponse({
            'status': 'success',
            'message': f"وضعیت {website.title} به {website.get_status_display} تغییر کرد.",
            'new_status': new_status,
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid status'}, status=400)


@require_POST
@staff_member_required
def edit_website_ajax(request, pk):
    """Handles saving edited website details"""
    website = get_object_or_404(Website, pk=pk)

    title = request.POST.get('title')
    url = request.POST.get('url')
    description = request.POST.get('description')
    category_id = request.POST.get('category')

    if not title or not url:
        return JsonResponse({'status': 'error', 'message': 'Title and URL are required'}, status=400)

    website.title = title
    website.url = url
    website.description = description
    if category_id:
        website.category_id = category_id

    website.save()
    return JsonResponse({
        'status': 'success',
        'message': 'وب‌سایت ویرایش شد.',
        'updated_title': website.title,
        'updated_url': website.url
    })


@require_POST
@staff_member_required
def resolve_report_ajax(request, pk):
    report = get_object_or_404(Report, pk=pk)
    report.is_resolved = True
    report.save()
    return JsonResponse({'status': 'success', 'message': "گزارش حل شد.", "resolved": True})


@require_POST
@staff_member_required
def add_category_ajax(request):
    name = request.POST.get('name')
    description = request.POST.get('description', '')
    icon = request.POST.get('icon', 'bi-folder')

    if not name:
        return JsonResponse(
            {'status': 'error', 'message': "نام دسته\u200cبندی الزامی است."}, status=400
        )

    from django.utils.text import slugify

    slug = slugify(name)
    if Category.objects.filter(slug=slug).exists():
        return JsonResponse(
            {'status': 'error', 'message': "این دسته\u200cبندی قبلاً وجود دارد."}, status=400
        )

    Category.objects.create(name=name, description=description, icon=icon)
    return JsonResponse({
        'status': 'success',
        'message': "دسته\u200cبندی اضافه شد!",
        "id": Category.objects.last().pk,
    })


@require_POST
@staff_member_required
def edit_category_ajax(request, pk):
    category = get_object_or_404(Category, pk=pk)
    name = request.POST.get('name')
    description = request.POST.get('description', '')
    icon = request.POST.get('icon', 'bi-folder')

    if not name:
        return JsonResponse({'status': 'error', 'message': "نام دسته‌بندی الزامی است."}, status=400)

    category.name = name
    category.description = description
    category.icon = icon
    category.save()

    return JsonResponse({
        'status': 'success',
        'message': "دسته‌بندی ویرایش شد.",
        'updated_name': category.name,
        'updated_icon': category.icon,
    })

@require_POST
@staff_member_required
def delete_category_ajax(request, pk):
    category = get_object_or_404(Category, pk=pk)

    # Check if category is in use
    if category.website_set.exists():
        return JsonResponse({
            'status': 'error',
            'message': f"این دسته‌بندی شامل {category.website_set.count()} وب‌سایت است. لطفاً ابتدا وب‌سایت‌ها را تغییر دهید.",
            },
            status=400,
        )

    category.delete()
    return JsonResponse({'status': 'success', 'message': "دسته‌بندی حذف شد."})


@user_passes_test(is_admin)
def add_tag(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Tag.objects.get_or_create(name=name)
            messages.success(request, 'برچسب اضافه شد!')
    return redirect('admin_dashboard')
