from functools import wraps

from django.urls import reverse
from django.db.models.manager import BaseManager
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponseForbidden, JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.db.models import Q, Count
from django.utils import timezone
from django_ratelimit.decorators import ratelimit
import json
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from .models import Website, Category, Rating, Review, Report
from .forms import (
    WebsiteSubmitForm,
    PublicWebsiteSubmitForm,
    RatingForm,
    ReviewForm,
    ReportForm,
    QuickSubmitForm,
)
from taggit.models import Tag
import random

def is_admin(user):
    return user.is_staff


def staff_ajax_required(view_func):
    protected_view = staff_member_required(view_func)

    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            return JsonResponse(
                {'status': 'error', 'message': 'شما اجازه انجام این عملیات را ندارید.'},
                status=403,
            )
        return protected_view(request, *args, **kwargs)

    return wrapped_view


def _soft_delete_website(website, actor, reason):
    website.is_deleted = True
    website.deleted_at = timezone.now()
    website.deleted_by = actor
    website.deletion_reason = (reason or '').strip()
    website.save(
        update_fields=('is_deleted', 'deleted_at', 'deleted_by', 'deletion_reason', 'updated_at')
    )


# ==================== Home Page ====================
def index(request):
    websites = Website.objects.filter(
        status=Website.STATUS_APPROVED,
        is_deleted=False,
    ).select_related('category')
    categories = Category.objects.annotate(
        website_count=Count(
            'website_set',
            filter=Q(
                website_set__status=Website.STATUS_APPROVED,
                website_set__is_deleted=False,
            ),
        )
    )
    all_tags = Tag.objects.annotate(
        website_count=Count(
            'websites_tagged',
            filter=Q(
                websites_tagged__status=Website.STATUS_APPROVED,
                websites_tagged__is_deleted=False,
            ),
        )
    ).order_by('-website_count')[:10]

    category_slug = request.GET.get('category')
    selected_category = None
    if category_slug:
        # Soft filter: unknown slug → empty list (200), not 404
        selected_category = Category.objects.filter(slug=category_slug).first()
        if selected_category:
            websites = websites.filter(category=selected_category)
        else:
            websites = websites.none()

    tag_slug = request.GET.get('tag')
    selected_tag = None
    if tag_slug:
        selected_tag = Tag.objects.filter(slug=tag_slug).first()
        if selected_tag:
            websites = websites.filter(tags__slug=tag_slug)
        else:
            websites = websites.none()

    search = request.GET.get('search')
    if search:
        websites = websites.filter(
            Q(title__icontains=search)
            | Q(description__icontains=search)
            | Q(tags__name__icontains=search)
        ).distinct()

    # Limit before shuffle — avoid loading the full approved table
    featured_qs = list(
        Website.objects.filter(status=Website.STATUS_APPROVED, is_deleted=False)
        .select_related('category')
        .order_by('-created_at')[:24]
    )
    random.shuffle(featured_qs)
    featured_websites = featured_qs[:6]

    paginator = Paginator(websites, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'all_tags': all_tags,
        'featured_websites': featured_websites,
        'category_slug': category_slug,
        'selected_category': selected_category,
        'tag_slug': tag_slug,
        'selected_tag': selected_tag,  # ✅ Now properly contains the Tag object
    }
    return render(request, 'directory/index.html', context)

def search_suggestions(request):
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'suggestions': []})

    websites = Website.objects.filter(
        status=Website.STATUS_APPROVED,
        is_deleted=False,
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
    website = get_object_or_404(
        Website.objects.select_related('category').prefetch_related('tags'),
        slug=slug,
    )
    is_owner = request.user.is_authenticated and website.created_by_id == request.user.id
    can_edit_website = is_owner or request.user.is_staff
    if website.is_deleted:
        if not can_edit_website:
            raise Http404
    elif website.status != Website.STATUS_APPROVED:
        raise Http404

    # Prefer shared tags (prefetch avoids extra tag-id query); fill with category
    tag_ids = [t.id for t in website.tags.all()]
    related_list = []
    if tag_ids and not website.is_deleted:
        related_list = list(
            Website.objects.filter(
                status=Website.STATUS_APPROVED,
                is_deleted=False,
                tags__id__in=tag_ids,
            )
            .exclude(id=website.id)
            .distinct()
            .select_related('category')[:4]
        )
    if len(related_list) < 4 and website.category_id:
        need = 4 - len(related_list)
        exclude_ids = [website.id] + [w.id for w in related_list]
        related_list.extend(
            list(
                Website.objects.filter(
                    status=Website.STATUS_APPROVED,
                    is_deleted=False,
                    category_id=website.category_id,
                )
                .exclude(id__in=exclude_ids)
                .select_related('category')[:need]
            )
        )
    related_websites = related_list

    reviews = website.reviews.filter(is_approved=True)[:10] if not website.is_deleted else []

    user_rating = None
    user_review = None
    user_report = None

    if request.user.is_authenticated and not website.is_deleted:
        user_rating = website.ratings.filter(user=request.user).first()
        user_review = website.reviews.filter(user=request.user).first()
        user_report = website.reports.filter(user=request.user).first()

    rating_form = RatingForm()
    review_form = ReviewForm()
    report_form = ReportForm()
    can_restore_website = (
        request.user.is_staff
        or (is_owner and website.deleted_by_id == request.user.id)
    )

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
        'can_edit_website': can_edit_website and not website.is_deleted,
        'can_restore_website': can_restore_website,
    }
    return render(request, 'directory/detail.html', context)

# ==================== Rating, Review, Report ====================
@login_required
@require_POST
@ratelimit(key='user', rate='20/m', method='POST', block=False)
def rate_website(request, slug):
    """Record 1–5 star rating. Ratelimit is advisory (block=False) so tests/dev never drop writes."""
    website = get_object_or_404(
        Website, slug=slug, status=Website.STATUS_APPROVED, is_deleted=False
    )
    rating_value = request.POST.get('rating')
    try:
        score = int(rating_value)
    except (TypeError, ValueError):
        messages.error(request, 'امتیاز نامعتبر است.')
        return redirect('website_detail', slug=slug)
    if score < 1 or score > 5:
        messages.error(request, 'امتیاز باید بین ۱ تا ۵ باشد.')
        return redirect('website_detail', slug=slug)

    Rating.objects.update_or_create(
        website=website,
        user=request.user,
        defaults={'rating': score},
    )
    website.update_rating()
    messages.success(request, 'امتیاز شما ثبت شد!')
    return redirect('website_detail', slug=slug)

@login_required
def review_website(request, slug):
    website = get_object_or_404(
        Website, slug=slug, status=Website.STATUS_APPROVED, is_deleted=False
    )
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            # taggit doesn't affect reviews directly, but ensure unique review per user if needed
            # Currently, the model allows multiple reviews per user.
            # If you want one review per user, add unique_together in Review model.
            Review.objects.create(
                website=website,
                user=request.user,
                content=form.cleaned_data['content'],
                is_approved=True
            )
            messages.success(request, 'نظر شما ثبت شد!')
    return redirect('website_detail', slug=slug)

@login_required
def report_website(request, slug):
    website = get_object_or_404(
        Website, slug=slug, status=Website.STATUS_APPROVED, is_deleted=False
    )
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

def _wants_json(request):
    """True for AJAX / fetch clients."""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return True
    accept = request.headers.get('Accept', '')
    return 'application/json' in accept and 'text/html' not in accept.split(',')[0]


def submit_website(request):
    """
    Public website submission.
    - Progressive enhancement: classic POST works without JS.
    - AJAX (fetch + X-Requested-With / Accept JSON): returns JSON.
    Uses PublicWebsiteSubmitForm (full fields + django-simple-captcha).
    """
    categories = Category.objects.all()

    if request.method == 'POST':
        form_data = request.POST
        if request.user.is_authenticated:
            form_data = request.POST.copy()
            form_data.pop('owner_name', None)
            form_data.pop('owner_email', None)
        form = PublicWebsiteSubmitForm(form_data)
        if form.is_valid():
            website = form.save(commit=False)
            website.status = Website.STATUS_PENDING
            if not website.description:
                website.description = 'ثبت شده توسط کاربر'
            if request.user.is_authenticated:
                website.created_by = request.user
                website.owner_name = (
                    request.user.get_full_name() or request.user.username
                )
                website.owner_email = request.user.email or ''
            else:
                if not website.owner_name:
                    website.owner_name = 'ناشناس'
            website.save()
            # Apply tags from form helper fields
            tags_input = form.cleaned_data.get('tags_input', '') or ''
            tag_names = [t.strip() for t in tags_input.split(',') if t.strip()]
            if tag_names:
                website.tags.set(tag_names)

            if _wants_json(request):
                return JsonResponse(
                    {
                        'status': 'success',
                        'message': 'وب‌سایت شما با موفقیت ثبت شد و در انتظار تأیید است.',
                        'redirect': reverse('success'),
                    }
                )
            messages.success(
                request, 'وب‌سایت شما با موفقیت ثبت شد و در انتظار تأیید است.'
            )
            return redirect('success')

        if _wants_json(request):
            return JsonResponse(
                {
                    'status': 'error',
                    'message': 'لطفاً اطلاعات را به درستی وارد کنید.',
                    'errors': {
                        f: [str(e) for e in errs] for f, errs in form.errors.items()
                    },
                },
                status=400,
            )
        messages.error(request, 'لطفا اطلاعات را به درستی وارد کنید.')
    else:
        form = PublicWebsiteSubmitForm()

    return render(
        request,
        'directory/submit.html',
        {'form': form, 'categories': categories},
    )


# ==================== Edit Website ====================

# ==================== Edit Website ====================
@login_required
def edit_website(request, slug):
    website = get_object_or_404(Website, slug=slug, is_deleted=False)
    if website.created_by != request.user and not request.user.is_staff:
        messages.error(request, 'شما اجازه ویرایش این وب‌سایت را ندارید.')
        return redirect('website_detail', slug=slug)

    if request.method == 'POST':
        form = WebsiteSubmitForm(request.POST, instance=website)
        if form.is_valid():
            prior_status = website.status
            updated = form.save(commit=False)
            if prior_status == Website.STATUS_APPROVED:
                updated.status = Website.STATUS_PENDING
                msg = (
                    'وب‌سایت با موفقیت ویرایش شد و برای بررسی دوباره '
                    'در انتظار تأیید قرار گرفت.'
                )
            else:
                updated.status = Website.STATUS_PENDING
                msg = 'وب‌سایت با موفقیت ویرایش شد و در انتظار تأیید است.'

            updated.save()
            tags_input = form.cleaned_data.get('tags_input', '') or ''
            tag_names = [t.strip() for t in tags_input.split(',') if t.strip()]
            if tag_names:
                updated.tags.set(tag_names)

            messages.success(request, msg)
            return redirect('user_dashboard')
    else:
        form = WebsiteSubmitForm(instance=website)

    categories = Category.objects.all()
    current_tags = ', '.join([tag.name for tag in website.tags.all()])

    return render(
        request,
        'directory/edit_website.html',
        {
            'form': form,
            'categories': categories,
            'website': website,
            'current_tags': current_tags,
            'current_tag_names': [tag.name for tag in website.tags.all()],
        },
    )

def success(request):
    return render(request, 'directory/success.html')

# ==================== Auth ====================
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            message = 'حساب کاربری شما ایجاد شد!'
            messages.success(request, message)
            if _wants_json(request):
                return JsonResponse({
                    'status': 'success',
                    'message': message,
                    'redirect': reverse('index'),
                })
            return redirect('index')
        if _wants_json(request):
            return JsonResponse(
                {
                    'status': 'error',
                    'message': 'لطفاً اطلاعات را به درستی وارد کنید.',
                    'errors': {
                        field: [str(error) for error in errors]
                        for field, errors in form.errors.items()
                    },
                },
                status=400,
            )
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
                message = 'خوش آمدید!'
                messages.success(request, message)
                if _wants_json(request):
                    return JsonResponse({
                        'status': 'success',
                        'message': message,
                        'redirect': reverse('index'),
                    })
                return redirect('index')
        if _wants_json(request):
            return JsonResponse(
                {
                    'status': 'error',
                    'message': 'لطفاً اطلاعات را به درستی وارد کنید.',
                    'errors': {
                        field: [str(error) for error in errors]
                        for field, errors in form.errors.items()
                    },
                },
                status=400,
            )
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
    my_websites = Website.objects.filter(created_by=request.user, is_deleted=False)
    deleted_websites = Website.objects.filter(
        created_by=request.user,
        is_deleted=True,
    ).select_related('deleted_by')
    my_ratings = Rating.objects.filter(user=request.user)
    my_reviews = Review.objects.filter(user=request.user)

    context = {
        'my_websites': my_websites,
        'deleted_websites': deleted_websites,
        'my_ratings': my_ratings,
        'my_reviews': my_reviews,
    }
    return render(request, 'directory/user_dashboard.html', context)

@login_required
@require_POST
def delete_my_website(request, pk):
    website = get_object_or_404(
        Website,
        pk=pk,
        created_by=request.user,
        is_deleted=False,
    )
    _soft_delete_website(website, request.user, request.POST.get('deletion_reason'))
    messages.success(request, 'وب‌سایت به بخش حذف‌شده‌ها منتقل شد.')
    return redirect('user_dashboard')


@login_required
@require_POST
def restore_my_website(request, pk):
    website = get_object_or_404(
        Website,
        pk=pk,
        created_by=request.user,
        is_deleted=True,
    )
    if website.deleted_by_id != request.user.id:
        return HttpResponseForbidden('شما اجازه بازگردانی این وب‌سایت را ندارید.')
    website.is_deleted = False
    website.save(update_fields=('is_deleted', 'updated_at'))
    messages.success(request, 'وب‌سایت به فهرست شما بازگردانده شد.')
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
    pending_websites = Website.objects.select_related('category').filter(
        status=Website.STATUS_PENDING,
        is_deleted=False,
    )
    approved_websites = Website.objects.select_related('category').filter(
        status=Website.STATUS_APPROVED,
        is_deleted=False,
    )
    rejected_websites = Website.objects.select_related('category').filter(
        status=Website.STATUS_REJECTED,
        is_deleted=False,
    )
    reports = Report.objects.select_related('website', 'user').filter(is_resolved=False)
    deleted_websites = Website.objects.filter(is_deleted=True).select_related(
        'category',
        'created_by',
        'deleted_by',
    )
    categories = Category.objects.annotate(
        website_count=Count('website_set', filter=Q(website_set__is_deleted=False))
    )
    tags = Tag.objects.annotate(
        website_count=Count(
            'websites_tagged',
            filter=Q(websites_tagged__is_deleted=False),
        )
    )
    users = User.objects.annotate(
        website_count=Count(
            'submitted_websites',
            filter=Q(submitted_websites__is_deleted=False),
            distinct=True,
        ),
        review_count=Count('review', distinct=True),
    ).order_by('-date_joined')[:5]
    recent_reviews = Review.objects.select_related('user', 'website').order_by(
        '-created_at'
    )[:10]

    # For the dashboard, we might want to count websites per tag
    # taggit handles this, but we can annotate if needed
    context = {
        'pending': pending_websites,
        'approved': approved_websites,
        'rejected': rejected_websites,
        'reports': reports,
        'categories': categories,
        'tags': tags,
        'deleted_websites': deleted_websites,
        'pending_count': pending_websites.count(),
        'report_count': reports.count(),
        'users': users,
        'recent_reviews': recent_reviews,
    }
    return render(request, 'directory/admin_dashboard.html', context)

@require_POST
@staff_ajax_required
def approve_website_ajax(request, pk):
    website = get_object_or_404(Website, pk=pk, is_deleted=False)
    website.status = Website.STATUS_APPROVED
    website.save()
    return JsonResponse({
        'status': 'success',
        'message': f'{website.title} تأیید شد!',
        'new_status': Website.STATUS_APPROVED,
    })

@require_POST
@staff_ajax_required
def reject_website_ajax(request, pk):
    website = get_object_or_404(Website, pk=pk, is_deleted=False)
    website.status = Website.STATUS_REJECTED
    website.save()
    return JsonResponse({
        'status': 'success',
        'message': f'{website.title} رد شد.',
        'new_status': Website.STATUS_REJECTED
    })

@require_POST
@staff_ajax_required
def delete_website_ajax(request, pk):
    website = get_object_or_404(Website, pk=pk, is_deleted=False)
    website_title = website.title
    _soft_delete_website(website, request.user, request.POST.get('deletion_reason'))
    return JsonResponse(
        {
            'status': 'success',
            'message': f'{website_title} به بخش حذف‌شده‌ها منتقل شد.',
            'deleted': True,
        }
    )

@require_POST
@staff_ajax_required
def restore_website_ajax(request, pk):
    website = get_object_or_404(Website, pk=pk, is_deleted=True)
    website.is_deleted = False
    website.save(update_fields=('is_deleted', 'updated_at'))
    return JsonResponse({
        'status': 'success',
        'message': f'{website.title} به فهرست وب‌سایت‌ها بازگردانده شد.',
        'restored': True,
    })

@require_POST
@staff_ajax_required
def update_website_status_ajax(request, pk):
    website = get_object_or_404(Website, pk=pk, is_deleted=False)
    new_status = request.POST.get('status')
    if new_status in {
        Website.STATUS_PENDING,
        Website.STATUS_APPROVED,
        Website.STATUS_REJECTED,
    }:
        website.status = new_status
        website.save()
        return JsonResponse({
            'status': 'success',
            'message': f"وضعیت {website.title} به {website.get_status_display} تغییر کرد.",
            'new_status': new_status,
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid status'}, status=400)

@require_POST
@staff_ajax_required
def edit_website_ajax(request, pk):
    website = get_object_or_404(Website, pk=pk, is_deleted=False)
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
@staff_ajax_required
def resolve_report_ajax(request, pk):
    report = get_object_or_404(Report, pk=pk)
    report.is_resolved = True
    report.save()
    return JsonResponse({'status': 'success', 'message': "گزارش حل شد.", "resolved": True})

@require_POST
@staff_ajax_required
def add_category_ajax(request):
    name = request.POST.get('name')
    description = request.POST.get('description', '')
    icon = request.POST.get('icon', 'bi-folder')

    if not name:
        return JsonResponse(
            {'status': 'error', 'message': "نام دسته‌بندی الزامی است."}, status=400
        )

    from django.utils.text import slugify
    slug = slugify(name)
    if Category.objects.filter(slug=slug).exists():
        return JsonResponse(
            {'status': 'error', 'message': "این دسته‌بندی قبلاً وجود دارد."}, status=400
        )

    Category.objects.create(name=name, description=description, icon=icon)
    return JsonResponse({
        'status': 'success',
        'message': "دسته‌بندی اضافه شد!",
        "id": Category.objects.last().pk,
    })

@require_POST
@staff_ajax_required
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
        'updated_id': category.pk,
    })

@require_POST
@staff_ajax_required
def delete_category_ajax(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if category.website_set.exists():
        return JsonResponse({
            'status': 'error',
            'message': f"این دسته‌بندی شامل {category.website_set.count()} وب‌سایت است.",
        }, status=400)
    category.delete()
    return JsonResponse({'status': 'success', 'message': "دسته‌بندی حذف شد."})

# Tag management is now mostly handled by taggit's admin or the form logic.
# We can keep a simple AJAX endpoint if needed, but often not required.
# If you still want to add tags via AJAX in admin:
@require_POST
@staff_ajax_required
def add_tag_ajax(request):
    """Handles creation of a new global tag"""
    tag_name = request.POST.get('tag_name')

    if not tag_name:
        return JsonResponse({'status': 'error', 'message': "نام برچسب الزامی است."}, status=400)

    # Create or get the tag
    tag, created = Tag.objects.get_or_create(name=tag_name)

    if created:
        return JsonResponse(
            {'status': 'success', 'message': f"برچسب '{tag.name}' ایجاد شد.", "id": tag.pk}
        )
    return JsonResponse(
        {'status': 'success', 'message': f"برچسب '{tag.name}' از قبل وجود داشت.", "id": tag.pk}
    )

@require_POST
@staff_ajax_required
def delete_tag_ajax(request, pk):
    """Handles deletion of a tag via AJAX"""
    tag = get_object_or_404(Tag, pk=pk)

    # Check if tag is in use
    # taggit: no reverse manager on Tag; query through Website.tags
    if Website.objects.filter(tags=tag).exists():
        count = Website.objects.filter(tags=tag).count()
        return JsonResponse(
            {
                'status': 'error',
                'message': (
                    f"این برچسب شامل {count} وب‌سایت است. "
                    "لطفاً ابتدا وب‌سایت‌ها را تغییر دهید."
                ),
            },
            status=400,
        )

    tag.delete()
    return JsonResponse({'status': 'success', 'message': "برچسب حذف شد."})


@require_POST
@staff_ajax_required
def edit_tag_ajax(request, pk):
    """Handles editing a tag via AJAX"""
    tag = get_object_or_404(Tag, pk=pk)
    name = request.POST.get('name')

    if not name:
        return JsonResponse({'status': 'error', 'message': "نام برچسب الزامی است."}, status=400)

    # Check for duplicate names (excluding current tag)
    if Tag.objects.filter(name=name).exclude(pk=pk).exists():
        return JsonResponse({'status': 'error', 'message': "این نام برچسب تکراری است."}, status=400)

    tag.name = name
    tag.save()

    return JsonResponse(
        {'status': 'success', 'message': "برچسب ویرایش شد.", "updated_name": tag.name}
    )
