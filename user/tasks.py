from django.core.mail import send_mail
from django.conf import settings

from celery import shared_task

@shared_task
def send_otp_code(otp_code, user_email):
    send_mail(
        subject='Welcome to TaskSphere',
        message=f'Your OTP code is {otp_code}. If you did not send this request, please ignore this email.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        fail_silently=False,
    )