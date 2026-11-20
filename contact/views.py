from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.contrib import messages
from django.http import JsonResponse
from directory.views import _wants_json
from .models import Contact
from .forms import ContactForm
# Create your views here.


class ContactFormView(FormView):
    """Show the Contact page."""

    form_class = ContactForm
    template_name = 'contact/contact.html'
    model = Contact
    success_message = 'از تماس شما سپاس‌‌گزاریم.'
    success_url = reverse_lazy('contact_page')
    # success_url = reverse_lazy('/contact/thanks.html')

    def form_valid(self, form):
        """Validate the form."""
        email = form.cleaned_data["email"]

        spam_email_list = Contact.objects.filter(spam_status=True)
        if email not in spam_email_list:
            form.save(commit=True)
            messages.success(self.request, self.success_message)
            if _wants_json(self.request):
                return JsonResponse({
                    'status': 'success',
                    'message': self.success_message,
                    'redirect': str(self.get_success_url()),
                })
            return super(ContactFormView, self).form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        """Show the Contact page."""
        if _wants_json(self.request):
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
        return render(self.request, 'contact/contact.html', {'form': form})
        # return super().form_invalid(form)
