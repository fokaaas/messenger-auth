import re

import bcrypt
from flask import Blueprint, render_template, request, session, redirect, url_for, flash

from app.services.database import get_user_by_phone, update_user_password
from app.services.otp_service import generate_otp, store_otp, verify_otp
from app.services.telegram_service import send_otp
from app.utils.validators import validate_password

recovery_bp = Blueprint("recovery", __name__)


@recovery_bp.route("/recover", methods=["GET", "POST"])
def recover():
    if request.method == "POST":
        phone = request.form.get("phone", "").strip()

        if not phone:
            return render_template("recover.html", error="Phone number is required.")

        user = get_user_by_phone(phone)
        if not user:
            return render_template("recover.html", error="No account found with this phone number.")

        if not user.get("chat_id"):
            return render_template("recover.html", error="No Telegram chat ID associated with this account.")

        otp_code = generate_otp()
        store_otp(phone, otp_code)

        if not send_otp(user["chat_id"], otp_code):
            return render_template("recover.html", error="Failed to send OTP via Telegram.")

        session["recover_phone"] = phone
        return redirect(url_for("recovery.verify"))

    return render_template("recover.html")


@recovery_bp.route("/recover/verify", methods=["GET", "POST"])
def verify():
    if "recover_phone" not in session:
        return redirect(url_for("recovery.recover"))

    if request.method == "POST":
        otp_code = request.form.get("otp", "").strip()

        if not otp_code or not re.match(r"^\d{6}$", otp_code):
            return render_template("recover_verify.html", error="Please enter a valid 6-digit code.")

        if not verify_otp(session["recover_phone"], otp_code):
            return render_template("recover_verify.html", error="Invalid or expired code. Please try again.")

        session["recover_otp_verified"] = True

        user = get_user_by_phone(session["recover_phone"])
        if user.get("pin_hash"):
            return redirect(url_for("recovery.pin"))
        else:
            session["recover_pin_verified"] = True
            return redirect(url_for("recovery.reset"))

    return render_template("recover_verify.html")


@recovery_bp.route("/recover/pin", methods=["GET", "POST"])
def pin():
    if not session.get("recover_otp_verified"):
        return redirect(url_for("recovery.recover"))

    user = get_user_by_phone(session["recover_phone"])

    if request.method == "POST":
        pin_input = request.form.get("pin", "").strip()

        if not pin_input:
            return render_template("recover_pin.html", error="Please enter your PIN.")

        if not bcrypt.checkpw(pin_input.encode("utf-8"), user["pin_hash"].encode("utf-8")):
            return render_template("recover_pin.html", error="Invalid PIN.")

        session["recover_pin_verified"] = True
        return redirect(url_for("recovery.reset"))

    return render_template("recover_pin.html")


@recovery_bp.route("/recover/reset", methods=["GET", "POST"])
def reset():
    if not session.get("recover_pin_verified"):
        return redirect(url_for("recovery.recover"))

    if request.method == "POST":
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        error = validate_password(password, confirm)
        if error:
            return render_template("recover_reset.html", error=error)

        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")
        update_user_password(session["recover_phone"], password_hash)

        session.clear()
        return render_template("login.html", success="Password reset successfully. Please log in.")

    return render_template("recover_reset.html")
