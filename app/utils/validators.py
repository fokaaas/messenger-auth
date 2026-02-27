import re


def validate_password(pwd, confirm):
    if pwd != confirm:
        return "Passwords do not match."
    if len(pwd) < 8:
        return "Password must be at least 8 characters."
    if not re.search(r"[A-Z]", pwd):
        return "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", pwd):
        return "Password must contain at least one lowercase letter."
    if not re.search(r"\d", pwd):
        return "Password must contain at least one digit."
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", pwd):
        return "Password must contain at least one special character."
    return None
