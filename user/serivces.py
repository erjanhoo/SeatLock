from random import random
from django.core.mail import send_mail


def generate_otp_code():
    otp = random(100000, 999999)
    return otp


def check_otp_code(entered_otp, user_otp):
    if entered_otp == user_otp:
        return True
    return False

