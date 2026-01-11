from random import randint



def generate_otp_code():
    otp = randint(100000, 999999)
    return str(otp)


def check_otp_code(entered_otp, user_otp):
    if entered_otp == user_otp:
        return True
    return False

