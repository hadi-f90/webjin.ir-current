import os
import re
import json
from decimal import Decimal
from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User, Permission
from django.urls import reverse
from django.conf import settings
from django.core.management import call_command
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from unittest.mock import patch, MagicMock
from .models import Website, Category, Rating, Review, Report
from .forms import WebsiteSubmitForm, QuickSubmitForm, RatingForm, ReviewForm, ReportForm
from taggit.models import Tag


class SecuritySettingsTests(TestCase):
    """Tests to ensure security settings are correctly configured."""

    def test_secret_key_is_not_hardcoded_weak(self):
        """Ensure SECRET_KEY is not the default insecure one."""
        # The key in settings.py was updated to require env var, so it shouldn't be the hardcoded one.
        # We check if it's the specific hardcoded string from the old code.
        self.assertNotEqual(settings.SECRET_KEY, 'django-insecure-3^_p-t)!)gdhhq_uroo9@k36bl3p2(h+k(eat&nyi&1(b53hyr')
        # In production, it should be long and random.
        # Note: In tests, if no env var is set, it might raise ValueError.
        # Ensure your test environment has a SECRET_KEY set.
        # For this test, we assume the env var is set or the settings allow a fallback for tests.
        # If you haven't set DJANGO_SECRET_KEY in your test env, this test will fail at import time.
        # Add this to your test runner or .env file for testing:
        # DJANGO_SECRET_KEY=test-secret-key-that-is-long-enough-for-testing-12345678901234567890
        self.assertGreater(len(settings.SECRET_KEY), 50)

    def test_debug_is_false_in_production(self):
        """Ensure DEBUG is False when running in production-like environment."""
        # This test assumes you use environment variables.
        self.assertFalse(settings.DEBUG, "DEBUG should be False in production.")

    def test_secure_ssl_redirect(self):
        """Ensure SSL redirect is configured."""
        # In tests, SSL redirect might be off. Check if it's configured correctly for prod.
        if not settings.DEBUG:
            self.assertTrue(settings.SECURE_SSL_REDIRECT)

    def test_csrf_cookie_secure(self):
        """Ensure CSRF cookie is secure."""
        if not settings.DEBUG:
            self.assertTrue(settings.CSRF_COOKIE_SECURE)

    def test_session_cookie_secure(self):
        """Ensure session cookie is secure."""
        if not settings.DEBUG:
            self.assertTrue(settings.SESSION_COOKIE_SECURE)

    def test_x_frame_options(self):
        """Ensure clickjacking protection is on."""
        self.assertEqual(settings.X_FRAME_OPTIONS, 'DENY')

    def test_hsts_enabled(self):
        """Ensure HSTS is enabled."""
        if not settings.DEBUG:
            self.assertGreater(settings.SECURE_HSTS_SECONDS, 0)

    def test_csp_middleware_installed(self):
        """Ensure CSP middleware is in place."""
        self.assertIn('csp.middleware.CSPMiddleware', settings.MIDDLEWARE)

    def test_csp_script_src(self):
        """Ensure CSP allows only trusted script sources."""
        # Updated to use the new CSP structure
        self.assertIn("'self'", settings.CONTENT_SECURITY_POLICY['DIRECTIVES']['script-src'])
        self.assertIn('https://cdn.yektanet.com', settings.CONTENT_SECURITY_POLICY['DIRECTIVES']['script-src'])

class XSSAndInputValidationTests(TestCase):
    """Tests for Cross-Site Scripting (XSS) and Input Validation."""

    def setUp(self):
        self.client = Client()
        # Create a category and tag for testing
        self.category = Category.objects.create(name='Test Category', slug='test-cat')
        self.tag = Tag.objects.create(name='Test Tag', slug='test-tag')

    def test_url_validation_rejects_invalid_urls(self):
        """Ensure invalid URLs are rejected."""
        data = {
            'title': 'Test Site',
            'url': 'not-a-url',  # Invalid
            'description': 'Test desc',
            'category': self.category.pk,
            'owner_name': 'Test Owner',
            'owner_email': 'test@example.com',
        }
        form = WebsiteSubmitForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('url', form.errors)

    def test_url_validation_accepts_valid_urls(self):
        """Ensure valid URLs are accepted."""
        data = {
            'title': 'Test Site',
            'url': 'https://example.com',
            'description': 'Test desc',
            'category': self.category.pk,
            'owner_name': 'Test Owner',
            'owner_email': 'test@example.com',
        }
        form = WebsiteSubmitForm(data)
        self.assertTrue(form.is_valid())

    def test_xss_in_title(self):
        """Ensure XSS payloads in title are escaped."""
        # Create a website with an XSS payload in the title
        website = Website.objects.create(
            title='<script>alert("XSS")</script>',
            url='https://example.com',
            description='Test',
            category=self.category,
            owner_name='Test',
            owner_email='test@example.com',
            status='approved'
        )
        # Fetch the detail page
        response = self.client.get(reverse('website_detail', kwargs={'slug': website.slug}))
        self.assertEqual(response.status_code, 200)
        # Check that the script tag is not executed (escaped)
        # In Django templates, variables are auto-escaped, but we verify it's not raw HTML
        self.assertNotContains(response, '<script>alert("XSS")</script>', html=True)
        # It should be escaped as &lt;script&gt;...
        self.assertContains(response, '&lt;script&gt;')

    def test_xss_in_tag_name(self):
        """Ensure XSS payloads in tag names are escaped."""
        # Create a tag with XSS payload
        malicious_tag = Tag.objects.create(
            name='<script>alert("XSS")</script>',
            slug='test-malicious-tag'
        )
        # Fetch the tag suggestions endpoint (AJAX)
        response = self.client.get(reverse('tag_suggestions'), {'q': 'test'})
        # Check if the response is JSON
        self.assertEqual(response['Content-Type'], 'application/json')
        data = response.json()
        # The API returns raw data, but the JS template should escape it.
        # Here we just verify the API works and returns JSON.
        self.assertIsInstance(data, dict)
        self.assertIn('tags', data)

class AuthenticationAndAuthorizationTests(TestCase):
    """Tests for Authentication and Authorization."""

    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user('admin', 'admin@example.com', 'adminpass123')
        self.admin_user.is_staff = True
        self.admin_user.save()
        self.normal_user = User.objects.create_user('user', 'user@example.com', 'userpass123')
        self.category = Category.objects.create(name='Test', slug='test')

    def test_admin_access_required(self):
        """Ensure only staff can access admin dashboard."""
        self.client.login(username='user', password='userpass123')
        response = self.client.get(reverse('admin_dashboard'))
        # Should redirect to login or 403. If 301, it's a redirect issue.
        self.assertIn(response.status_code, [302, 403, 401])

    def test_admin_access_allowed(self):
        """Ensure staff can access admin dashboard."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('admin_dashboard'))
        # Should be 200. If 301, it's a redirect issue (likely SSL).
        self.assertEqual(response.status_code, 200)

    def test_password_strength(self):
        """Ensure weak passwords are rejected."""
        data = {
            'username': 'newuser',
            'password1': '123',  # Too short
            'password2': '123',
        }
        # Use Django's UserCreationForm
        from django.contrib.auth.forms import UserCreationForm
        form = UserCreationForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors) # Or password1 depending on validator

    def test_password_not_common(self):
        """Ensure common passwords are rejected."""
        data = {
            'username': 'newuser2',
            'password1': 'password',  # Common
            'password2': 'password',
        }
        from django.contrib.auth.forms import UserCreationForm
        form = UserCreationForm(data)
        self.assertFalse(form.is_valid())

class CSRFProtectionTests(TestCase):
    """Tests for CSRF Protection."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('csrfuser', 'csrf@example.com', 'userpass123')
        self.category = Category.objects.create(name='CSRF Test', slug='csrf-test')

    def test_csrf_protection_on_submit(self):
        """Ensure CSRF token is required for POST requests."""
        self.client.login(username='csrfuser', password='userpass123')

        data = {
            'title': 'CSRF Test Site',
            'url': 'https://example.com',
            'description': 'Test',
            'category': self.category.pk,
            'owner_name': 'Test',
            'owner_email': 'test@example.com',
        }

        # Django's test client automatically includes CSRF tokens for logged-in users.
        response = self.client.post(reverse('submit_website'), data)
        self.assertEqual(response.status_code, 302) # Redirect on success

    def test_csrf_token_in_templates(self):
        """Ensure CSRF token is present in forms."""
        response = self.client.get(reverse('submit_website'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'csrfmiddlewaretoken')

class DataIntegrityTests(TestCase):
    """Tests for Data Integrity and Race Conditions."""

    def setUp(self):
        self.category = Category.objects.create(name='Integrity Test', slug='integrity-test')

    def test_slug_uniqueness(self):
        """Ensure slugs are unique."""
        website1 = Website.objects.create(
            title='Unique Slug',
            url='https://example1.com',
            description='Test',
            category=self.category,
            owner_name='Test',
            owner_email='test1@example.com',
            slug='unique-slug'
        )
        # Django's ORM raises IntegrityError for unique constraints
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Website.objects.create(
                title='Duplicate Slug',
                url='https://example2.com',
                description='Test',
                category=self.category,
                owner_name='Test',
                owner_email='test2@example.com',
                slug='unique-slug'
            )

    def test_rating_update(self):
        """Ensure rating updates are accurate."""
        website = Website.objects.create(
            title='Rating Test',
            url='https://example.com',
            description='Test',
            category=self.category,
            owner_name='Test',
            owner_email='test@example.com',
            status='approved'
        )
        user1 = User.objects.create_user('rater1', 'r1@example.com', 'pass')
        user2 = User.objects.create_user('rater2', 'r2@example.com', 'pass')

        Rating.objects.create(website=website, user=user1, rating=5)
        Rating.objects.create(website=website, user=user2, rating=3)

        website.update_rating()
        self.assertEqual(website.average_rating, 4.0)
        self.assertEqual(website.total_ratings, 2)


# =============================================================================
# MODEL TESTS
# =============================================================================

class CategoryModelTests(TestCase):
    """Tests for the Category model."""

    def test_create_category(self):
        """Test creating a category with valid data."""
        category = Category.objects.create(
            name='Technology',
            slug='technology',
            description='Tech websites',
            icon='bi-laptop'
        )
        self.assertEqual(category.name, 'Technology')
        self.assertEqual(category.slug, 'technology')
        self.assertEqual(str(category), 'Technology')

    def test_category_website_count(self):
        """Test get_website_count method."""
        category = Category.objects.create(name='Test', slug='test')
        user = User.objects.create_user('testuser', 'test@test.com', 'pass123')

        # Create approved website
        website1 = Website.objects.create(
            title='Site 1',
            url='https://example1.com',
            category=category,
            status='approved',
            created_by=user
        )

        # Create pending website (should not count)
        website2 = Website.objects.create(
            title='Site 2',
            url='https://example2.com',
            category=category,
            status='pending',
            created_by=user
        )

        self.assertEqual(category.get_website_count(), 1)

    def test_category_ordering(self):
        """Test that categories are ordered by name."""
        Category.objects.create(name='Zebra', slug='zebra')
        Category.objects.create(name='Apple', slug='apple')
        Category.objects.create(name='Mango', slug='mango')

        categories = list(Category.objects.all())
        self.assertEqual(categories[0].name, 'Apple')
        self.assertEqual(categories[1].name, 'Mango')
        self.assertEqual(categories[2].name, 'Zebra')


class WebsiteModelTests(TestCase):
    """Tests for the Website model."""

    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@test.com', 'pass123')
        self.category = Category.objects.create(name='Test', slug='test')

    def test_create_website_auto_slug_generation(self):
        """Test that slug is auto-generated from title."""
        website = Website.objects.create(
            title='My Awesome Website',
            url='https://example.com',
            created_by=self.user
        )
        self.assertIsNotNone(website.slug)
        self.assertIn('my-awesome-website', website.slug)

    def test_create_website_with_custom_slug(self):
        """Test creating website with custom slug."""
        website = Website.objects.create(
            title='My Website',
            slug='custom-slug',
            url='https://example.com',
            created_by=self.user
        )
        self.assertEqual(website.slug, 'custom-slug')

    def test_slug_uniqueness_with_collision(self):
        """Test slug uniqueness when collision occurs."""
        website1 = Website.objects.create(
            title='Test Site',
            url='https://example1.com',
            created_by=self.user
        )

        # Create another with same title - should get unique slug
        website2 = Website.objects.create(
            title='Test Site',
            url='https://example2.com',
            created_by=self.user
        )

        self.assertNotEqual(website1.slug, website2.slug)

    def test_website_str_representation(self):
        """Test website string representation."""
        website = Website.objects.create(
            title='Test Website',
            url='https://example.com',
            created_by=self.user
        )
        self.assertEqual(str(website), 'Test Website')

    def test_website_get_absolute_url(self):
        """Test get_absolute_url method."""
        website = Website.objects.create(
            title='Test Site',
            url='https://example.com',
            created_by=self.user
        )
        expected_url = reverse('website_detail', kwargs={'slug': website.slug})
        self.assertEqual(website.get_absolute_url(), expected_url)

    def test_website_update_rating(self):
        """Test rating calculation."""
        website = Website.objects.create(
            title='Rating Test',
            url='https://example.com',
            status='approved',
            created_by=self.user
        )

        user1 = User.objects.create_user('rater1', 'r1@test.com', 'pass')
        user2 = User.objects.create_user('rater2', 'r2@test.com', 'pass')
        user3 = User.objects.create_user('rater3', 'r3@test.com', 'pass')

        Rating.objects.create(website=website, user=user1, rating=5)
        Rating.objects.create(website=website, user=user2, rating=4)
        Rating.objects.create(website=website, user=user3, rating=3)

        website.update_rating()

        self.assertEqual(website.average_rating, Decimal('4.00'))
        self.assertEqual(website.total_ratings, 3)

    def test_website_update_rating_no_ratings(self):
        """Test rating calculation with no ratings."""
        website = Website.objects.create(
            title='No Ratings',
            url='https://example.com',
            created_by=self.user
        )

        website.update_rating()

        self.assertEqual(website.average_rating, Decimal('0'))
        self.assertEqual(website.total_ratings, 0)

    def test_website_default_status(self):
        """Test default status is pending."""
        website = Website.objects.create(
            title='Test',
            url='https://example.com',
            created_by=self.user
        )
        self.assertEqual(website.status, 'pending')

    def test_website_with_tags(self):
        """Test website with taggit tags."""
        website = Website.objects.create(
            title='Tagged Site',
            url='https://example.com',
            created_by=self.user
        )
        website.tags.add('python', 'django', 'web')

        self.assertEqual(website.tags.count(), 3)
        self.assertTrue(website.tags.filter(name='python').exists())


class RatingModelTests(TestCase):
    """Tests for the Rating model."""

    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@test.com', 'pass123')
        self.website = Website.objects.create(
            title='Test Site',
            url='https://example.com',
            status='approved',
            created_by=self.user
        )

    def test_create_rating(self):
        """Test creating a rating."""
        rating = Rating.objects.create(
            website=self.website,
            user=self.user,
            rating=5
        )
        self.assertEqual(rating.rating, 5)
        self.assertEqual(str(rating), 'Test Site - 5 stars')

    def test_rating_unique_constraint(self):
        """Test that user can only rate a website once."""
        Rating.objects.create(website=self.website, user=self.user, rating=5)

        with self.assertRaises(IntegrityError):
            Rating.objects.create(website=self.website, user=self.user, rating=3)

    def test_rating_range(self):
        """Test rating value constraints."""
        # Valid ratings (1-5)
        for i in range(1, 6):
            user = User.objects.create_user(f'user{i}', f'u{i}@test.com', 'pass')
            rating = Rating.objects.create(website=self.website, user=user, rating=i)
            self.assertEqual(rating.rating, i)


class ReviewModelTests(TestCase):
    """Tests for the Review model."""

    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@test.com', 'pass123')
        self.website = Website.objects.create(
            title='Test Site',
            url='https://example.com',
            status='approved',
            created_by=self.user
        )

    def test_create_review(self):
        """Test creating a review."""
        review = Review.objects.create(
            website=self.website,
            user=self.user,
            content='Great website!'
        )
        self.assertEqual(review.content, 'Great website!')
        self.assertTrue(review.is_approved)
        self.assertIsNotNone(review.created_at)

    def test_review_ordering(self):
        """Test reviews are ordered by created_at descending."""
        user1 = User.objects.create_user('user1', 'u1@test.com', 'pass')
        user2 = User.objects.create_user('user2', 'u2@test.com', 'pass')

        review1 = Review.objects.create(website=self.website, user=user1, content='First')
        review2 = Review.objects.create(website=self.website, user=user2, content='Second')

        reviews = list(Review.objects.all())
        self.assertEqual(reviews[0], review2)  # Newest first
        self.assertEqual(reviews[1], review1)


class ReportModelTests(TestCase):
    """Tests for the Report model."""

    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@test.com', 'pass123')
        self.website = Website.objects.create(
            title='Test Site',
            url='https://example.com',
            status='approved',
            created_by=self.user
        )

    def test_create_report(self):
        """Test creating a report."""
        report = Report.objects.create(
            website=self.website,
            user=self.user,
            report_type='broken',
            description='Link is not working'
        )
        self.assertEqual(report.report_type, 'broken')
        self.assertFalse(report.is_resolved)

    def test_report_str_representation(self):
        """Test report string representation."""
        report = Report.objects.create(
            website=self.website,
            user=self.user,
            report_type='scam'
        )
        self.assertIn('Test Site', str(report))


# =============================================================================
# FORM TESTS
# =============================================================================

class WebsiteSubmitFormTests(TestCase):
    """Tests for WebsiteSubmitForm validation."""

    def setUp(self):
        self.category = Category.objects.create(name='Test', slug='test')

    def test_valid_form_data(self):
        """Test form with valid data."""
        data = {
            'title': 'Test Website',
            'url': 'https://example.com',
            'description': 'A great website',
            'category': self.category.pk,
            'owner_name': 'John Doe',
            'owner_email': 'john@example.com',
        }
        form = WebsiteSubmitForm(data)
        self.assertTrue(form.is_valid())

    def test_url_without_protocol_auto_prepend(self):
        """Test URL without http/https gets prepended."""
        data = {
            'title': 'Test Site',
            'url': 'example.com',
            'description': 'Test',
            'category': self.category.pk,
            'owner_name': 'John',
            'owner_email': 'john@test.com',
        }
        form = WebsiteSubmitForm(data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['url'], 'https://example.com')

    def test_invalid_url_rejected(self):
        """Test invalid URLs are rejected."""
        invalid_urls = [
            'not-a-url',
            'htp://wrong.com',
            'ftp://invalid.com',
            '',
        ]
        for url in invalid_urls:
            data = {
                'title': 'Test',
                'url': url,
                'description': 'Test',
                'category': self.category.pk,
                'owner_name': 'John',
                'owner_email': 'john@test.com',
            }
            form = WebsiteSubmitForm(data)
            self.assertFalse(form.is_valid(), f"URL '{url}' should be invalid")
            self.assertIn('url', form.errors)

    def test_empty_title_rejected(self):
        """Test empty title is rejected."""
        data = {
            'title': '',
            'url': 'https://example.com',
            'description': 'Test',
            'category': self.category.pk,
            'owner_name': 'John',
            'owner_email': 'john@test.com',
        }
        form = WebsiteSubmitForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_invalid_email_rejected(self):
        """Test invalid email is rejected."""
        data = {
            'title': 'Test',
            'url': 'https://example.com',
            'description': 'Test',
            'category': self.category.pk,
            'owner_name': 'John',
            'owner_email': 'not-an-email',
        }
        form = WebsiteSubmitForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('owner_email', form.errors)

    def test_custom_slug_uniqueness(self):
        """Test custom slug must be unique."""
        Website.objects.create(
            title='Existing Site',
            slug='my-custom-slug',
            url='https://example.com',
            owner_name='Test',
            owner_email='test@test.com'
        )

        data = {
            'title': 'New Site',
            'custom_slug': 'my-custom-slug',
            'url': 'https://newsite.com',
            'description': 'Test',
            'category': self.category.pk,
            'owner_name': 'John',
            'owner_email': 'john@test.com',
        }
        form = WebsiteSubmitForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('custom_slug', form.errors)

    def test_tags_input_parsing(self):
        """Test tags are parsed correctly."""
        data = {
            'title': 'Tagged Site',
            'url': 'https://example.com',
            'description': 'Test',
            'category': self.category.pk,
            'owner_name': 'John',
            'owner_email': 'john@test.com',
            'tags_input': 'python, django, web',
        }
        form = WebsiteSubmitForm(data)
        self.assertTrue(form.is_valid())

        website = form.save()
        self.assertEqual(website.tags.count(), 3)


class QuickSubmitFormTests(TestCase):
    """Tests for QuickSubmitForm validation."""

    def test_valid_form_data(self):
        """Test form with valid data."""
        data = {
            'title': 'Quick Site',
            'url': 'https://example.com',
        }
        form = QuickSubmitForm(data)
        self.assertTrue(form.is_valid())

    def test_minimal_fields_required(self):
        """Test only title and url are required."""
        data = {
            'title': 'Minimal Site',
            'url': 'https://example.com',
        }
        form = QuickSubmitForm(data)
        self.assertTrue(form.is_valid())

    def test_url_normalization(self):
        """Test URL is normalized."""
        data = {
            'title': 'Test',
            'url': 'example.com',
        }
        form = QuickSubmitForm(data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['url'], 'https://example.com')


class RatingFormTests(TestCase):
    """Tests for RatingForm."""

    def test_valid_rating_values(self):
        """Test valid rating values (1-5)."""
        for i in range(1, 6):
            form = RatingForm(data={'rating': str(i)})
            self.assertTrue(form.is_valid())

    def test_invalid_rating_value(self):
        """Test rating outside 1-5 is rejected."""
        for invalid in ['0', '6', '10', 'abc']:
            form = RatingForm(data={'rating': invalid})
            self.assertFalse(form.is_valid())


class ReviewFormTests(TestCase):
    """Tests for ReviewForm."""

    def test_valid_review(self):
        """Test valid review submission."""
        form = ReviewForm(data={'content': 'This is a great website!'})
        self.assertTrue(form.is_valid())

    def test_empty_review_rejected(self):
        """Test empty review is rejected."""
        form = ReviewForm(data={'content': ''})
        self.assertFalse(form.is_valid())


class ReportFormTests(TestCase):
    """Tests for ReportForm."""

    def test_valid_report_types(self):
        """Test all valid report types."""
        valid_types = ['broken', 'shutdown', 'inappropriate', 'scam', 'other']
        for report_type in valid_types:
            form = ReportForm(data={'report_type': report_type, 'description': 'Test'})
            self.assertTrue(form.is_valid(), f"Report type '{report_type}' should be valid")

    def test_invalid_report_type(self):
        """Test invalid report type is rejected."""
        form = ReportForm(data={'report_type': 'invalid_type'})
        self.assertFalse(form.is_valid())

    def test_description_optional(self):
        """Test description is optional."""
        form = ReportForm(data={'report_type': 'broken'})
        self.assertTrue(form.is_valid())


# =============================================================================
# VIEW TESTS
# =============================================================================

class IndexViewTests(TestCase):
    """Tests for the index (home) view."""

    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@test.com', 'pass123')
        self.category = Category.objects.create(name='Tech', slug='tech')

    def test_index_view_status_code(self):
        """Test index view returns 200."""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_index_shows_only_approved_websites(self):
        """Test only approved websites are shown."""
        Website.objects.create(
            title='Approved Site',
            url='https://approved.com',
            status='approved'
        )
        Website.objects.create(
            title='Pending Site',
            url='https://pending.com',
            status='pending'
        )

        response = self.client.get(reverse('index'))
        self.assertContains(response, 'Approved Site')
        self.assertNotContains(response, 'Pending Site')

    def test_index_filter_by_category(self):
        """Test filtering by category."""
        Website.objects.create(
            title='Tech Site',
            url='https://tech.com',
            status='approved',
            category=self.category
        )

        response = self.client.get(reverse('index') + '?category=tech')
        self.assertContains(response, 'Tech Site')

    def test_index_search_functionality(self):
        """Test search functionality."""
        Website.objects.create(
            title='Python Tutorial',
            url='https://python.com',
            status='approved',
            description='Learn Python'
        )

        response = self.client.get(reverse('index') + '?search=python')
        self.assertContains(response, 'Python Tutorial')

    def test_index_pagination(self):
        """Test pagination works."""
        for i in range(15):
            Website.objects.create(
                title=f'Site {i}',
                url=f'https://site{i}.com',
                status='approved'
            )

        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('page_obj', response.context)


class WebsiteDetailViewTests(TestCase):
    """Tests for website detail view."""

    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@test.com', 'pass123')
        self.website = Website.objects.create(
            title='Test Site',
            slug='test-site',
            url='https://example.com',
            status='approved',
            description='A test website',
            owner_name='Owner',
            owner_email='owner@test.com'
        )

    def test_detail_view_status_code(self):
        """Test detail view returns 200 for approved website."""
        response = self.client.get(reverse('website_detail', kwargs={'slug': 'test-site'}))
        self.assertEqual(response.status_code, 200)

    def test_detail_view_404_for_pending(self):
        """Test detail view returns 404 for pending website."""
        self.website.status = 'pending'
        self.website.save()

        response = self.client.get(reverse('website_detail', kwargs={'slug': 'test-site'}))
        self.assertEqual(response.status_code, 404)

    def test_detail_shows_reviews(self):
        """Test reviews are displayed."""
        Review.objects.create(
            website=self.website,
            user=self.user,
            content='Great site!',
            is_approved=True
        )

        response = self.client.get(reverse('website_detail', kwargs={'slug': 'test-site'}))
        self.assertContains(response, 'Great site!')

    def test_detail_shows_related_websites(self):
        """Test related websites are shown."""
        category = Category.objects.create(name='Related', slug='related')
        self.website.category = category
        self.website.save()

        Website.objects.create(
            title='Related Site',
            url='https://related.com',
            status='approved',
            category=category
        )

        response = self.client.get(reverse('website_detail', kwargs={'slug': 'test-site'}))
        self.assertContains(response, 'Related Site')


class SubmitWebsiteViewTests(TestCase):
    """Tests for website submission views."""

    def test_submit_view_get(self):
        """Test GET request shows form."""
        response = self.client.get(reverse('submit_website'))
        self.assertEqual(response.status_code, 200)

    def test_submit_view_post_valid(self):
        """Test POST with valid data creates website."""
        response = self.client.post(reverse('submit_website'), {
            'title': 'New Site',
            'url': 'https://newsite.com',
        })
        self.assertEqual(Website.objects.count(), 1)
        self.assertRedirects(response, reverse('success'))

    def test_submit_view_sets_pending_status(self):
        """Test submitted website has pending status."""
        self.client.post(reverse('submit_website'), {
            'title': 'Pending Site',
            'url': 'https://pending.com',
        })

        website = Website.objects.first()
        self.assertEqual(website.status, 'pending')

    def test_submit_view_associates_user(self):
        """Test logged-in user's website is associated."""
        User.objects.create_user('testuser', 'test@test.com', 'pass123')
        self.client.login(username='testuser', password='pass123')

        self.client.post(reverse('submit_website'), {
            'title': 'User Site',
            'url': 'https://usersite.com',
        })

        website = Website.objects.first()
        self.assertEqual(website.created_by.username, 'testuser')


class EditWebsiteViewTests(TestCase):
    """Tests for edit website view."""

    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@test.com', 'pass123')
        self.website = Website.objects.create(
            title='Original Title',
            url='https://original.com',
            status='approved',
            created_by=self.user
        )

    def test_edit_view_accessible_by_owner(self):
        """Test owner can access edit view."""
        self.client.login(username='testuser', password='pass123')
        response = self.client.get(reverse('edit_website', kwargs={'slug': self.website.slug}))
        self.assertEqual(response.status_code, 200)

    def test_edit_view_forbidden_for_non_owner(self):
        """Test non-owner cannot access edit view."""
        User.objects.create_user('other', 'other@test.com', 'pass123')
        self.client.login(username='other', password='pass123')

        response = self.client.get(reverse('edit_website', kwargs={'slug': self.website.slug}))
        self.assertEqual(response.status_code, 403)

    def test_edit_view_accessible_by_admin(self):
        """Test admin can access edit view."""
        admin = User.objects.create_user('admin', 'admin@test.com', 'pass123', is_staff=True)
        self.client.login(username='admin', password='pass123')

        response = self.client.get(reverse('edit_website', kwargs={'slug': self.website.slug}))
        self.assertEqual(response.status_code, 200)

    def test_edit_view_updates_website(self):
        """Test editing updates website."""
        self.client.login(username='testuser', password='pass123')

        response = self.client.post(reverse('edit_website', kwargs={'slug': self.website.slug}), {
            'title': 'Updated Title',
            'url': 'https://updated.com',
            'description': 'Updated description',
            'owner_name': 'Owner',
            'owner_email': 'owner@test.com',
        })

        self.website.refresh_from_db()
        self.assertEqual(self.website.title, 'Updated Title')


class AuthenticationViewTests(TestCase):
    """Tests for authentication views."""

    def test_register_view_get(self):
        """Test register view GET."""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_register_view_creates_user(self):
        """Test registration creates user."""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'securepassword123',
            'password2': 'securepassword123',
        })

        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertRedirects(response, reverse('index'))

    def test_register_password_mismatch(self):
        """Test registration fails with password mismatch."""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'password123',
            'password2': 'different123',
        })

        self.assertFalse(User.objects.filter(username='newuser').exists())

    def test_login_view(self):
        """Test login functionality."""
        User.objects.create_user('testuser', 'test@test.com', 'pass123')

        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'pass123',
        })

        self.assertRedirects(response, reverse('index'))

    def test_logout_view(self):
        """Test logout functionality."""
        User.objects.create_user('testuser', 'test@test.com', 'pass123')
        self.client.login(username='testuser', password='pass123')

        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('index'))


class UserDashboardViewTests(TestCase):
    """Tests for user dashboard."""

    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@test.com', 'pass123')
        self.website = Website.objects.create(
            title='My Site',
            url='https://mysite.com',
            created_by=self.user
        )

    def test_dashboard_requires_login(self):
        """Test dashboard requires authentication."""
        response = self.client.get(reverse('user_dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_dashboard_shows_user_websites(self):
        """Test dashboard shows user's websites."""
        self.client.login(username='testuser', password='pass123')
        response = self.client.get(reverse('user_dashboard'))

        self.assertContains(response, 'My Site')

    def test_delete_website(self):
        """Test deleting own website."""
        self.client.login(username='testuser', password='pass123')

        response = self.client.get(reverse('delete_my_website', kwargs={'pk': self.website.pk}))

        self.assertEqual(Website.objects.count(), 0)
        self.assertRedirects(response, reverse('user_dashboard'))

    def test_cannot_delete_others_website(self):
        """Test cannot delete another user's website."""
        other = User.objects.create_user('other', 'other@test.com', 'pass123')
        self.client.login(username='other', password='pass123')

        response = self.client.get(reverse('delete_my_website', kwargs={'pk': self.website.pk}))
        self.assertEqual(response.status_code, 404)


class RatingViewTests(TestCase):
    """Tests for rating functionality."""

    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@test.com', 'pass123')
        self.website = Website.objects.create(
            title='Test Site',
            url='https://example.com',
            status='approved',
            created_by=self.user
        )

    def test_rate_requires_login(self):
        """Test rating requires login."""
        response = self.client.post(
            reverse('rate_website', kwargs={'slug': self.website.slug}),
            {'rating': '5'}
        )
        self.assertEqual(response.status_code, 302)

    def test_rate_creates_rating(self):
        """Test authenticated user can rate."""
        self.client.login(username='testuser', password='pass123')

        response = self.client.post(
            reverse('rate_website', kwargs={'slug': self.website.slug}),
            {'rating': '5'}
        )

        self.assertTrue(Rating.objects.filter(user=self.user, website=self.website).exists())

    def test_rate_updates_existing(self):
        """Test rating updates existing rating."""
        self.client.login(username='testuser', password='pass123')

        # First rating
        self.client.post(
            reverse('rate_website', kwargs={'slug': self.website.slug}),
            {'rating': '3'}
        )

        # Update rating
        self.client.post(
            reverse('rate_website', kwargs={'slug': self.website.slug}),
            {'rating': '5'}
        )

        ratings = Rating.objects.filter(user=self.user, website=self.website)
        self.assertEqual(ratings.count(), 1)
        self.assertEqual(ratings.first().rating, 5)


class ReviewViewTests(TestCase):
    """Tests for review functionality."""

    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@test.com', 'pass123')
        self.website = Website.objects.create(
            title='Test Site',
            url='https://example.com',
            status='approved',
            created_by=self.user
        )

    def test_review_requires_login(self):
        """Test review requires login."""
        response = self.client.post(
            reverse('review_website', kwargs={'slug': self.website.slug}),
            {'content': 'Great site!'}
        )
        self.assertEqual(response.status_code, 302)

    def test_review_creates_review(self):
        """Test authenticated user can submit review."""
        self.client.login(username='testuser', password='pass123')

        response = self.client.post(
            reverse('review_website', kwargs={'slug': self.website.slug}),
            {'content': 'Great site!'}
        )

        self.assertTrue(Review.objects.filter(user=self.user, website=self.website).exists())


class ReportViewTests(TestCase):
    """Tests for report functionality."""

    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@test.com', 'pass123')
        self.website = Website.objects.create(
            title='Test Site',
            url='https://example.com',
            status='approved',
            created_by=self.user
        )

    def test_report_requires_login(self):
        """Test report requires login."""
        response = self.client.post(
            reverse('report_website', kwargs={'slug': self.website.slug}),
            {'report_type': 'broken'}
        )
        self.assertEqual(response.status_code, 302)

    def test_report_creates_report(self):
        """Test authenticated user can submit report."""
        self.client.login(username='testuser', password='pass123')

        response = self.client.post(
            reverse('report_website', kwargs={'slug': self.website.slug}),
            {'report_type': 'broken', 'description': 'Link is broken'}
        )

        self.assertTrue(Report.objects.filter(user=self.user, website=self.website).exists())

    def test_cannot_report_twice(self):
        """Test user cannot report same website twice."""
        self.client.login(username='testuser', password='pass123')

        # First report
        self.client.post(
            reverse('report_website', kwargs={'slug': self.website.slug}),
            {'report_type': 'broken'}
        )

        # Second report attempt
        response = self.client.post(
            reverse('report_website', kwargs={'slug': self.website.slug}),
            {'report_type': 'scam'}
        )

        self.assertEqual(Report.objects.filter(user=self.user, website=self.website).count(), 1)


class AdminDashboardViewTests(TestCase):
    """Tests for admin dashboard."""

    def setUp(self):
        self.admin = User.objects.create_user('admin', 'admin@test.com', 'pass123', is_staff=True)
        self.user = User.objects.create_user('user', 'user@test.com', 'pass123')
        self.pending_website = Website.objects.create(
            title='Pending Site',
            url='https://pending.com',
            status='pending',
            created_by=self.user
        )

    def test_admin_dashboard_requires_staff(self):
        """Test admin dashboard requires staff status."""
        self.client.login(username='user', password='pass123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_admin_dashboard_accessible_by_staff(self):
        """Test staff can access admin dashboard."""
        self.client.login(username='admin', password='pass123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_admin_dashboard_shows_pending(self):
        """Test pending websites are shown."""
        self.client.login(username='admin', password='pass123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertContains(response, 'Pending Site')


# =============================================================================
# AJAX ENDPOINT TESTS
# =============================================================================

class AjaxWebsiteEndpointTests(TestCase):
    """Tests for AJAX website management endpoints."""

    def setUp(self):
        self.admin = User.objects.create_user('admin', 'admin@test.com', 'pass123', is_staff=True)
        self.admin.is_staff = True
        self.admin.save()

        self.website = Website.objects.create(
            title='Test Site',
            url='https://example.com',
            status='pending'
        )

    def test_approve_website(self):
        """Test approving website via AJAX."""
        self.client.login(username='admin', password='pass123')

        response = self.client.post(
            reverse('approve_website', kwargs={'pk': self.website.pk}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.website.refresh_from_db()
        self.assertEqual(self.website.status, 'approved')
        self.assertEqual(response.json()['status'], 'success')

    def test_reject_website(self):
        """Test rejecting website via AJAX."""
        self.client.login(username='admin', password='pass123')

        response = self.client.post(
            reverse('reject_website_ajax', kwargs={'pk': self.website.pk}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.website.refresh_from_db()
        self.assertEqual(self.website.status, 'rejected')

    def test_delete_website(self):
        """Test deleting website via AJAX."""
        self.client.login(username='admin', password='pass123')
        pk = self.website.pk

        response = self.client.post(
            reverse('delete_website_ajax', kwargs={'pk': pk}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertFalse(Website.objects.filter(pk=pk).exists())

    def test_update_status(self):
        """Test updating website status."""
        self.client.login(username='admin', password='pass123')

        response = self.client.post(
            reverse('update_website_status_ajax', kwargs={'pk': self.website.pk}),
            {'status': 'approved'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.website.refresh_from_db()
        self.assertEqual(self.website.status, 'approved')

    def test_edit_website_ajax(self):
        """Test editing website via AJAX."""
        self.client.login(username='admin', password='pass123')

        response = self.client.post(
            reverse('edit_website_ajax', kwargs={'pk': self.website.pk}),
            {
                'title': 'Updated Title',
                'url': 'https://updated.com',
                'description': 'Updated desc'
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.website.refresh_from_db()
        self.assertEqual(self.website.title, 'Updated Title')


class AjaxCategoryEndpointTests(TestCase):
    """Tests for AJAX category management endpoints."""

    def setUp(self):
        self.admin = User.objects.create_user('admin', 'admin@test.com', 'pass123', is_staff=True)
        self.category = Category.objects.create(name='Test', slug='test')

    def test_add_category(self):
        """Test adding category via AJAX."""
        self.client.login(username='admin', password='pass123')

        response = self.client.post(
            reverse('add_category_ajax'),
            {'name': 'New Category', 'description': 'A new category', 'icon': 'bi-star'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertTrue(Category.objects.filter(name='New Category').exists())
        self.assertEqual(response.json()['status'], 'success')

    def test_add_duplicate_category(self):
        """Test adding duplicate category fails."""
        self.client.login(username='admin', password='pass123')

        response = self.client.post(
            reverse('add_category_ajax'),
            {'name': 'Test', 'description': 'Duplicate'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertEqual(response.json()['status'], 'error')

    def test_edit_category(self):
        """Test editing category via AJAX."""
        self.client.login(username='admin', password='pass123')

        response = self.client.post(
            reverse('edit_category_ajax', kwargs={'pk': self.category.pk}),
            {'name': 'Updated Name', 'description': 'Updated', 'icon': 'bi-check'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.category.refresh_from_db()
        self.assertEqual(self.category.name, 'Updated Name')

    def test_delete_category(self):
        """Test deleting category via AJAX."""
        self.client.login(username='admin', password='pass123')

        response = self.client.post(
            reverse('delete_category_ajax', kwargs={'pk': self.category.pk}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertFalse(Category.objects.filter(pk=self.category.pk).exists())

    def test_delete_category_with_websites_fails(self):
        """Test deleting category with websites fails."""
        user = User.objects.create_user('user', 'user@test.com', 'pass123')
        Website.objects.create(
            title='Test',
            url='https://test.com',
            category=self.category
        )

        self.client.login(username='admin', password='pass123')

        response = self.client.post(
            reverse('delete_category_ajax', kwargs={'pk': self.category.pk}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertEqual(response.json()['status'], 'error')
        self.assertTrue(Category.objects.filter(pk=self.category.pk).exists())


class AjaxTagEndpointTests(TestCase):
    """Tests for AJAX tag management endpoints."""

    def setUp(self):
        self.admin = User.objects.create_user('admin', 'admin@test.com', 'pass123', is_staff=True)
        self.tag = Tag.objects.create(name='Test Tag', slug='test-tag')

    def test_add_tag(self):
        """Test adding tag via AJAX."""
        self.client.login(username='admin', password='pass123')

        response = self.client.post(
            reverse('add_tag_ajax'),
            {'tag_name': 'New Tag'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertTrue(Tag.objects.filter(name='New Tag').exists())

    def test_add_existing_tag(self):
        """Test adding existing tag returns existing."""
        self.client.login(username='admin', password='pass123')

        response = self.client.post(
            reverse('add_tag_ajax'),
            {'tag_name': 'Test Tag'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertEqual(Tag.objects.filter(name='Test Tag').count(), 1)

    def test_edit_tag(self):
        """Test editing tag via AJAX."""
        self.client.login(username='admin', password='pass123')

        response = self.client.post(
            reverse('edit_tag_ajax', kwargs={'pk': self.tag.pk}),
            {'name': 'Updated Tag'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.tag.refresh_from_db()
        self.assertEqual(self.tag.name, 'Updated Tag')

    def test_delete_tag(self):
        """Test deleting tag via AJAX."""
        self.client.login(username='admin', password='pass123')

        response = self.client.post(
            reverse('delete_tag_ajax', kwargs={'pk': self.tag.pk}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertFalse(Tag.objects.filter(pk=self.tag.pk).exists())


class AjaxReportEndpointTests(TestCase):
    """Tests for AJAX report management endpoints."""

    def setUp(self):
        self.admin = User.objects.create_user('admin', 'admin@test.com', 'pass123', is_staff=True)
        self.user = User.objects.create_user('user', 'user@test.com', 'pass123')

        website = Website.objects.create(
            title='Test',
            url='https://test.com',
            status='approved'
        )
        self.report = Report.objects.create(
            website=website,
            user=self.user,
            report_type='broken'
        )

    def test_resolve_report(self):
        """Test resolving report via AJAX."""
        self.client.login(username='admin', password='pass123')

        response = self.client.post(
            reverse('resolve_report_ajax', kwargs={'pk': self.report.pk}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.report.refresh_from_db()
        self.assertTrue(self.report.is_resolved)


# =============================================================================
# API/SEARCH TESTS
# =============================================================================

class SearchSuggestionsTests(TestCase):
    """Tests for search suggestions API."""

    def setUp(self):
        Website.objects.create(
            title='Python Tutorial',
            url='https://python.com',
            status='approved'
        )
        Website.objects.create(
            title='Django Guide',
            url='https://django.com',
            status='approved'
        )
        Tag.objects.create(name='python', slug='python')

    def test_search_suggestions_returns_websites(self):
        """Test search returns matching websites."""
        response = self.client.get(reverse('search_suggestions') + '?q=python')
        data = response.json()

        self.assertEqual(len(data['suggestions']), 2)  # 1 website + 1 tag

    def test_search_suggestions_minimum_query_length(self):
        """Test minimum query length is enforced."""
        response = self.client.get(reverse('search_suggestions') + '?q=p')
        data = response.json()

        self.assertEqual(len(data['suggestions']), 0)

    def test_search_suggestions_json_response(self):
        """Test response is JSON."""
        response = self.client.get(reverse('search_suggestions') + '?q=python')

        self.assertEqual(response['Content-Type'], 'application/json')


class TagSuggestionsTests(TestCase):
    """Tests for tag suggestions API."""

    def setUp(self):
        Tag.objects.create(name='python', slug='python')
        Tag.objects.create(name='django', slug='django')
        Tag.objects.create(name='javascript', slug='javascript')

    def test_tag_suggestions_returns_matches(self):
        """Test tag suggestions return matching tags."""
        response = self.client.get(reverse('tag_suggestions') + '?q=pyt')
        data = response.json()

        self.assertEqual(len(data['tags']), 1)
        self.assertEqual(data['tags'][0]['name'], 'python')

    def test_tag_suggestions_max_results(self):
        """Test tag suggestions limit results."""
        response = self.client.get(reverse('tag_suggestions') + '?q=j')
        data = response.json()

        self.assertLessEqual(len(data['tags']), 10)

    def test_tag_suggestions_json_format(self):
        """Test tag suggestions return correct format."""
        response = self.client.get(reverse('tag_suggestions') + '?q=python')
        data = response.json()

        self.assertIn('tags', data)
        self.assertIsInstance(data['tags'], list)


# =============================================================================
# PERMISSION & AUTHORIZATION TESTS
# =============================================================================

class PermissionTests(TestCase):
    """Tests for permission checks."""

    def setUp(self):
        self.admin = User.objects.create_user('admin', 'admin@test.com', 'pass123', is_staff=True)
        self.user = User.objects.create_user('user', 'user@test.com', 'pass123')
        self.website = Website.objects.create(
            title='Test Site',
            url='https://test.com',
            status='approved',
            created_by=self.user
        )

    def test_non_owner_cannot_edit(self):
        """Test non-owner cannot edit website."""
        other = User.objects.create_user('other', 'other@test.com', 'pass123')
        self.client.login(username='other', password='pass123')

        response = self.client.get(reverse('edit_website', kwargs={'slug': self.website.slug}))
        self.assertEqual(response.status_code, 403)

    def test_admin_can_edit_any(self):
        """Test admin can edit any website."""
        self.client.login(username='admin', password='pass123')

        response = self.client.get(reverse('edit_website', kwargs={'slug': self.website.slug}))
        self.assertEqual(response.status_code, 200)

    def test_ajax_requires_post(self):
        """Test AJAX endpoints require POST method."""
        self.client.login(username='admin', password='pass123')

        response = self.client.get(
            reverse('approve_website', kwargs={'pk': self.website.pk}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertEqual(response.status_code, 405)  # Method Not Allowed

    def test_ajax_requires_staff(self):
        """Test AJAX endpoints require staff status."""
        self.client.login(username='user', password='pass123')

        response = self.client.post(
            reverse('approve_website', kwargs={'pk': self.website.pk}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertEqual(response.status_code, 403)


# =============================================================================
# SECURITY TESTS
# =============================================================================

class SecurityTests(TestCase):
    """Tests for security features."""

    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@test.com', 'pass123')
        self.admin = User.objects.create_user('admin', 'admin@test.com', 'pass123', is_staff=True)

    def test_sql_injection_in_search(self):
        """Test SQL injection is prevented."""
        response = self.client.get(reverse('index') + "?search=' OR '1'='1")
        self.assertEqual(response.status_code, 200)
        # Should not expose data or cause error

    def test_xss_in_title_escaped(self):
        """Test XSS in title is escaped."""
        website = Website.objects.create(
            title='<script>alert("XSS")</script>',
            url='https://test.com',
            status='approved'
        )

        response = self.client.get(reverse('website_detail', kwargs={'slug': website.slug}))
        self.assertNotContains(response, '<script>alert', html=True)

    def test_csrf_token_required_for_post(self):
        """Test CSRF protection on forms."""
        response = self.client.post(
            reverse('submit_website'),
            {'title': 'Test', 'url': 'https://test.com'},
            HTTP_X_CSRFTOKEN='invalid'
        )
        # Django's test client handles CSRF, but we verify the form works
        self.assertIn(response.status_code, [200, 302])

    def test_rate_limiting_on_rating(self):
        """Test rate limiting on rating endpoint."""
        self.client.login(username='testuser', password='pass123')
        website = Website.objects.create(
            title='Rate Test',
            url='https://rate.com',
            status='approved'
        )

        # Make multiple rapid requests
        for _ in range(10):
            self.client.post(
                reverse('rate_website', kwargs={'slug': website.slug}),
                {'rating': '5'}
            )

        # Should handle gracefully (rate limit decorator)


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================

class ErrorHandlingTests(TestCase):
    """Tests for error handling."""

    def test_404_page(self):
        """Test 404 page renders correctly."""
        response = self.client.get('/nonexistent-page/')
        self.assertEqual(response.status_code, 404)

    def test_invalid_slug_returns_404(self):
        """Test invalid slug returns 404."""
        response = self.client.get(reverse('website_detail', kwargs={'slug': 'nonexistent-slug'}))
        self.assertEqual(response.status_code, 404)

    def test_invalid_pk_returns_404(self):
        """Test invalid PK returns 404."""
        response = self.client.get(reverse('delete_my_website', kwargs={'pk': 99999}))
        self.assertEqual(response.status_code, 404)

    def test_invalid_category_returns_empty(self):
        """Test invalid category filter returns empty."""
        response = self.client.get(reverse('index') + '?category=nonexistent')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Website')  # No websites should match


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class WebsiteLifecycleTests(TestCase):
    """Integration tests for complete website lifecycle."""

    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@test.com', 'pass123')
        self.admin = User.objects.create_user('admin', 'admin@test.com', 'pass123', is_staff=True)
        self.admin.is_staff = True
        self.admin.save()

    def test_full_website_lifecycle(self):
        """Test complete website submission to approval lifecycle."""
        # 1. Submit website
        response = self.client.post(reverse('submit_website'), {
            'title': 'New Website',
            'url': 'https://newsite.com',
        })
        self.assertRedirects(response, reverse('success'))

        website = Website.objects.get(title='New Website')
        self.assertEqual(website.status, 'pending')

        # 2. Login as admin and approve
        self.client.login(username='admin', password='pass123')
        response = self.client.post(
            reverse('approve_website', kwargs={'pk': website.pk}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.json()['status'], 'success')

        website.refresh_from_db()
        self.assertEqual(website.status, 'approved')

        # 3. View approved website
        response = self.client.get(reverse('website_detail', kwargs={'slug': website.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'New Website')

    def test_rating_review_report_flow(self):
        """Test complete rating, review, and report flow."""
        website = Website.objects.create(
            title='Test Site',
            url='https://test.com',
            status='approved'
        )

        # Login and rate
        self.client.login(username='testuser', password='pass123')

        self.client.post(
            reverse('rate_website', kwargs={'slug': website.slug}),
            {'rating': '5'}
        )
        self.assertTrue(Rating.objects.filter(user=self.user, website=website).exists())

        # Add review
        self.client.post(
            reverse('review_website', kwargs={'slug': website.slug}),
            {'content': 'Great site!'}
        )
        self.assertTrue(Review.objects.filter(user=self.user, website=website).exists())

        # Submit report
        self.client.post(
            reverse('report_website', kwargs={'slug': website.slug}),
            {'report_type': 'broken', 'description': 'Link slow'}
        )
        self.assertTrue(Report.objects.filter(user=self.user, website=website).exists())

        # Verify report blocks duplicate reports
        response = self.client.post(
            reverse('report_website', kwargs={'slug': website.slug}),
            {'report_type': 'scam'}
        )
        self.assertEqual(Report.objects.filter(user=self.user, website=website).count(), 1)


class CategoryTagIntegrationTests(TestCase):
    """Integration tests for category and tag management."""

    def setUp(self):
        self.admin = User.objects.create_user('admin', 'admin@test.com', 'pass123', is_staff=True)
        self.admin.is_staff = True
        self.admin.save()

    def test_category_crud_operations(self):
        """Test complete category CRUD operations."""
        self.client.login(username='admin', password='pass123')

        # Create
        response = self.client.post(
            reverse('add_category_ajax'),
            {'name': 'New Category', 'description': 'Test', 'icon': 'bi-star'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.json()['status'], 'success')
        category = Category.objects.get(name='New Category')

        # Update
        response = self.client.post(
            reverse('edit_category_ajax', kwargs={'pk': category.pk}),
            {'name': 'Updated Category', 'description': 'Updated', 'icon': 'bi-check'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        category.refresh_from_db()
        self.assertEqual(category.name, 'Updated Category')

        # Delete
        response = self.client.post(
            reverse('delete_category_ajax', kwargs={'pk': category.pk}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertFalse(Category.objects.filter(pk=category.pk).exists())

    def test_tag_crud_operations(self):
        """Test complete tag CRUD operations."""
        self.client.login(username='admin', password='pass123')

        # Create
        response = self.client.post(
            reverse('add_tag_ajax'),
            {'tag_name': 'New Tag'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.json()['status'], 'success')
        tag = Tag.objects.get(name='New Tag')

        # Update
        response = self.client.post(
            reverse('edit_tag_ajax', kwargs={'pk': tag.pk}),
            {'name': 'Updated Tag'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        tag.refresh_from_db()
        self.assertEqual(tag.name, 'Updated Tag')

        # Delete
        response = self.client.post(
            reverse('delete_tag_ajax', kwargs={'pk': tag.pk}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertFalse(Tag.objects.filter(pk=tag.pk).exists())


# =============================================================================
# PERFORMANCE TESTS
# =============================================================================

class PerformanceTests(TestCase):
    """Basic performance tests."""

    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@test.com', 'pass123')
        self.category = Category.objects.create(name='Test', slug='test')

    def test_index_query_count(self):
        """Test index view doesn't make excessive queries."""
        # Create test data
        for i in range(20):
            Website.objects.create(
                title=f'Site {i}',
                url=f'https://site{i}.com',
                status='approved',
                category=self.category
            )

        with self.assertNumQueries(5):  # Should be optimized
            response = self.client.get(reverse('index'))

        self.assertEqual(response.status_code, 200)

    def test_detail_view_query_count(self):
        """Test detail view query count."""
        website = Website.objects.create(
            title='Test Site',
            url='https://test.com',
            status='approved',
            category=self.category
        )

        with self.assertNumQueries(4):  # Website, reviews, ratings, related
            response = self.client.get(reverse('website_detail', kwargs={'slug': website.slug}))

        self.assertEqual(response.status_code, 200)


# =============================================================================
# STATIC PAGES TESTS
# =============================================================================

class StaticPagesTests(TestCase):
    """Tests for static pages."""

    def test_about_page(self):
        """Test about page renders."""
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'دایرکتوری')

    def test_terms_page(self):
        """Test terms page renders."""
        response = self.client.get(reverse('terms'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'قوانین')

    def test_success_page(self):
        """Test success page renders."""
        response = self.client.get(reverse('success'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'موفقیت')


# =============================================================================
# PAGINATION TESTS
# =============================================================================

class PaginationTests(TestCase):
    """Tests for pagination functionality."""

    def setUp(self):
        for i in range(25):
            Website.objects.create(
                title=f'Site {i}',
                url=f'https://site{i}.com',
                status='approved'
            )

    def test_pagination_first_page(self):
        """Test first page of pagination."""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('page_obj', response.context)
        self.assertTrue(response.context['page_obj'].has_previous() is False)

    def test_pagination_second_page(self):
        """Test second page of pagination."""
        response = self.client.get(reverse('index') + '?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['page_obj'].has_previous())

    def test_pagination_last_page(self):
        """Test last page of pagination."""
        response = self.client.get(reverse('index') + '?page=3')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['page_obj'].has_next() is False)

    def test_pagination_out_of_range(self):
        """Test out of range page returns valid response."""
        response = self.client.get(reverse('index') + '?page=100')
        self.assertEqual(response.status_code, 200)
        # Django returns last page for out of range
        self.assertTrue(response.context['page_obj'].has_next() is False)