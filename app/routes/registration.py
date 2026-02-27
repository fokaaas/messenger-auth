import io
import base64
import re

import bcrypt
import pyotp
import qrcode
from flask import Blueprint, render_template, request, session, redirect, url_for

from app.services.database import save_user, get_user_by_phone
from app.services.otp_service import generate_otp, store_otp, verify_otp
from app.services.telegram_service import send_otp
from app.utils.validators import validate_password

registration_bp = Blueprint("registration", __name__)


@registration_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        phone = request.form.get("phone", "").strip()
        chat_id = request.form.get("chat_id", "").strip()

        if not phone or not chat_id:
            return render_template("register.html", error="Both fields are required.")

        if not re.match(r"^\+?\d{7,15}$", phone):
            return render_template("register.html", error="Invalid phone number format.")

        if get_user_by_phone(phone):
            return render_template("register.html", error="This phone number is already registered.")

        otp_code = generate_otp()
        store_otp(phone, otp_code)

        if not send_otp(chat_id, otp_code):
            return render_template("register.html", error="Failed to send OTP via Telegram. Check your chat ID.")

        session["phone"] = phone
        session["chat_id"] = chat_id
        return redirect(url_for("registration.verify"))

    return render_template("register.html")


@registration_bp.route("/verify", methods=["GET", "POST"])
def verify():
    if "phone" not in session:
        return redirect(url_for("registration.register"))

    if request.method == "POST":
        otp_code = request.form.get("otp", "").strip()

        if not otp_code or not re.match(r"^\d{6}$", otp_code):
            return render_template("verify.html", error="Please enter a valid 6-digit code.")

        if not verify_otp(session["phone"], otp_code):
            return render_template("verify.html", error="Invalid or expired code. Please try again.")

        session["verified"] = True
        return redirect(url_for("registration.password"))

    return render_template("verify.html")


@registration_bp.route("/password", methods=["GET", "POST"])
def password():
    if not session.get("verified"):
        return redirect(url_for("registration.register"))

    if request.method == "POST":
        pwd = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        error = validate_password(pwd, confirm)
        if error:
            return render_template("password.html", error=error)

        password_hash = bcrypt.hashpw(pwd.encode("utf-8"), bcrypt.gensalt(rounds=12))
        session["password_hash"] = password_hash.decode("utf-8")
        return redirect(url_for("registration.setup_2fa"))

    return render_template("password.html")


@registration_bp.route("/setup-2fa")
def setup_2fa():
    if not session.get("password_hash"):
        return redirect(url_for("registration.register"))

    totp_secret = pyotp.random_base32()
    session["totp_secret"] = totp_secret

    phone = session["phone"]
    totp = pyotp.TOTP(totp_secret)
    provisioning_uri = totp.provisioning_uri(name=phone, issuer_name="MessengerApp")

    img = qrcode.make(provisioning_uri)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return render_template("setup_2fa.html", qr_code=qr_base64, provisioning_uri=provisioning_uri)


@registration_bp.route("/confirm-2fa", methods=["POST"])
def confirm_2fa():
    if not session.get("totp_secret"):
        return redirect(url_for("registration.register"))

    totp_code = request.form.get("totp_code", "").strip()
    totp_secret = session["totp_secret"]
    totp = pyotp.TOTP(totp_secret)

    if not totp.verify(totp_code):
        phone = session["phone"]
        provisioning_uri = totp.provisioning_uri(name=phone, issuer_name="MessengerApp")
        img = qrcode.make(provisioning_uri)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return render_template("setup_2fa.html", qr_code=qr_base64, provisioning_uri=provisioning_uri,
                               error="Invalid code. Please try again.")

    save_user(
        phone=session["phone"],
        password_hash=session["password_hash"],
        totp_secret=totp_secret,
        chat_id=session.get("chat_id"),
    )

    session.clear()
    return redirect(url_for("registration.complete"))


@registration_bp.route("/complete")
def complete():
    return render_template("complete.html")
