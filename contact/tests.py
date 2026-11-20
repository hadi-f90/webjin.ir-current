from django.test import TestCase
from django.contrib.messages import get_messages
from django.urls import reverse
from unittest.mock import patch

from .models import Contact


class ContactFormFeedbackTests(TestCase):
    """Cover contact AJAX feedback and its ordinary HTML POST fallback."""

    def test_ajax_invalid_fields_and_captcha_return_field_errors(self):
        response = self.client.post(
            reverse('contact_page'),
            {},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        payload = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(payload['status'], 'error')
        self.assertEqual(payload['message'], 'لطفاً اطلاعات را به درستی وارد کنید.')
        for field in ('name', 'email', 'message', 'captcha'):
            with self.subTest(field=field):
                self.assertIn(field, payload['errors'])
                self.assertIsInstance(payload['errors'][field], list)
                self.assertTrue(payload['errors'][field])
        self.assertEqual(Contact.objects.count(), 0)

    @patch('captcha.fields.CaptchaField.clean', return_value='human')
    def test_ajax_success_saves_once_and_queues_visible_message(self, _captcha_clean):
        response = self.client.post(
            reverse('contact_page'),
            {
                'name': 'Test Person',
                'email': 'person@example.com',
                'subject': '0',
                'message': 'A message for the WebJin team.',
                'captcha_0': 'test-key',
                'captcha_1': 'human',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        payload = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload['status'], 'success')
        self.assertEqual(payload['redirect'], reverse('contact_page'))
        self.assertTrue(payload['message'])
        self.assertEqual(Contact.objects.count(), 1)
        saved_contact = Contact.objects.get()
        self.assertEqual(saved_contact.email, 'person@example.com')
        queued_messages = list(get_messages(response.wsgi_request))
        self.assertEqual([message.message for message in queued_messages], [payload['message']])

    def test_html_invalid_post_rerenders_form_with_errors(self):
        response = self.client.post(reverse('contact_page'), {})

        self.assertEqual(response.status_code, 200)
        self.assertIn('name', response.context['form'].errors)
        self.assertIn('email', response.context['form'].errors)
        self.assertIn('captcha', response.context['form'].errors)
        self.assertEqual(Contact.objects.count(), 0)

    @patch('captcha.fields.CaptchaField.clean', return_value='human')
    def test_html_success_post_redirects_and_queues_success_message(self, _captcha_clean):
        response = self.client.post(
            reverse('contact_page'),
            {
                'name': 'HTML Person',
                'email': 'html-person@example.com',
                'subject': '0',
                'message': 'An ordinary HTML form submission.',
                'captcha_0': 'test-key',
                'captcha_1': 'human',
            },
        )

        self.assertRedirects(response, reverse('contact_page'), fetch_redirect_response=False)
        self.assertEqual(Contact.objects.count(), 1)
        queued_messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(queued_messages), 1)
        self.assertTrue(queued_messages[0].message)
