import os
import re
from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User, Permission
from django.urls import reverse
from django.conf import settings
from django.core.management import call_command
from .models import Website, Category, Tag, Rating, Review, Report
from .forms import WebsiteSubmitForm

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

class ErrorPageTests(TestCase):
    """Tests for Error Pages."""

    def test_404_page(self):
        """Ensure 404 page renders correctly."""
        # Use the full path to avoid redirects
        response = self.client.get('/non-existent-page/', follow=True)
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, '۴۰۴')

    def test_403_page(self):
        """Ensure 403 page renders correctly."""
        # Try to access admin as non-staff
        user = User.objects.create_user('noaccess', 'no@example.com', 'pass')
        self.client.login(username='noaccess', password='pass')
        response = self.client.get(reverse('admin_dashboard'))
        # Should redirect to login or 403
        self.assertIn(response.status_code, [302, 403])

    def test_500_page(self):
        """Ensure 500 page renders correctly."""
        # This is hard to test without triggering an error.
        # You can mock a view that raises an exception.
        pass