from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from .forms import WebsiteSubmitForm
from .models import Category, Website
import logging

logger = logging.getLogger(__name__)

def submit_website(request):
    logger.error('Form import: {}', WebsiteSubmitForm)
    logger.error('Form fields: {}', WebsiteSubmitForm._meta.model)

def is_admin(user):
    return user.is_staff

def index(request):
    # Get all approved websites
    websites = Website.objects.filter(status='approved')
    categories = Category.objects.all()

    # Filter by category
    category_slug = request.GET.get('category')
    if category_slug:
        websites = websites.filter(category__slug=category_slug)

    # Search
    search = request.GET.get('search')
    if search:
        websites = websites.filter(title__icontains=search) | websites.filter(
            description__icontains=search
        )

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
    related_websites = Website.objects.filter(category=website.category, status='approved').exclude(
        id=website.id
    )[:4]

    context = {
        'website': website,
        'related_websites': related_websites,
    }
    return render(request, 'directory/detail.html', context)

def submit_website(request):
    if request.method == 'POST':
        form = WebsiteSubmitForm(request.POST)
        if form.is_valid():
            website = form.save(commit=False)
            website.status = 'pending'
            if request.user.is_authenticated:
                website.created_by = request.user
            website.save()
            messages.success(request, "وب‌سایت شما با موفقیت ثبت شد!")
            return redirect('success')
    else:
        form = WebsiteSubmitForm()

    categories = Category.objects.all()
    return render(request, 'directory/submit.html', {'form': form, 'categories': categories})


def success(request):
    return render(request, 'directory/success.html')

@user_passes_test(is_admin)
def admin_dashboard(request):
    pending_websites = Website.objects.filter(status='pending')
    approved_websites = Website.objects.filter(status='approved')
    rejected_websites = Website.objects.filter(status='rejected')

    context = {
        'pending': pending_websites,
        'approved': approved_websites,
        'rejected': rejected_websites,
    }
    return render(request, 'directory/admin_dashboard.html', context)

@user_passes_test(is_admin)
def approve_website(request, pk):
    website = get_object_or_404(Website, pk=pk)
    website.status = 'approved'
    website.save()
    messages.success(request, f'{website.title} has been approved!')
    return redirect('admin_dashboard')

@user_passes_test(is_admin)
def reject_website(request, pk):
    website = get_object_or_404(Website, pk=pk)
    website.status = 'rejected'
    website.save()
    messages.warning(request, f'{website.title} has been rejected.')
    return redirect('admin_dashboard')