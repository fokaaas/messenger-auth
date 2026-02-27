import secrets
import time

_otp_store = {}

OTP_EXPIRY_SECONDS = 300


def generate_otp():
    return f"{secrets.randbelow(900000) + 100000}"


def store_otp(phone, code):
    _otp_store[phone] = {
        "code": code,
        "created_at": time.time(),
    }


def verify_otp(phone, code):
    entry = _otp_store.get(phone)
    if not entry:
        return False
    if time.time() - entry["created_at"] > OTP_EXPIRY_SECONDS:
        _otp_store.pop(phone, None)
        return False
    if entry["code"] == code:
        _otp_store.pop(phone, None)
        return True
    return False
