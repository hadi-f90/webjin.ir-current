from django.db import models

SPAM_STATUS = (
    (-1, 'Not Specified'),
    (0, 'OK'),
    (1, "Spam"),
)

SUBJECTS = (
    (0, 'درخواست کمک'),
    (1, 'گزارش اشکال'),
    (2, 'پیشنهاد همکاری'),
    (3, 'انتقاد و ایده برای بهبود'),
)


class Contact(models.Model):
    """A contact page model."""

    name = models.CharField(help_text='مانند آیدین ',
                            max_length=20, verbose_name="نام")

    email = models.EmailField(
        help_text='مثل: yourname@xyz.com',
        verbose_name="رایانامه")

    subject = models.IntegerField(
        choices=SUBJECTS, default=0, verbose_name="موضوع", help_text="علّت تماس شما")

    datetime_created = models.DateTimeField(
        auto_now_add=True, verbose_name="تاریخ")

    message = models.TextField(help_text='جاپیامی', verbose_name="پیام")
    spam_status = models.IntegerField(
        choices=SPAM_STATUS, default=-1, verbose_name="وضعیّت پیام")

    def __str__(self):
        """Return a string representation of the model."""
        return self.name
