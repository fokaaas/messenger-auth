import re
import time

import bcrypt
import pyotp
from flask import Blueprint, render_template, request, session, redirect, url_for

from app.services.database import get_user_by_phone, update_user_pin
from app.utils.auth import require_auth

login_bp = Blueprint("login", __name__)


@login_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")

        if not phone or not password:
            return render_template("login.html", error="Both fields are required.")

        user = get_user_by_phone(phone)
        if not user:
            return render_template("login.html", error="Invalid phone number or password.")

        if not bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8")):
            return render_template("login.html", error="Invalid phone number or password.")

        session["login_phone"] = phone
        session["login_2fa_pending"] = True
        return redirect(url_for("login.two_factor"))

    return render_template("login.html")


@login_bp.route("/login/2fa", methods=["GET", "POST"])
def two_factor():
    if not session.get("login_2fa_pending"):
        return redirect(url_for("login.login"))

    phone = session.get("login_phone")
    user = get_user_by_phone(phone)

    if request.method == "POST":
        totp_code = request.form.get("totp_code", "").strip()

        if not totp_code or not re.match(r"^\d{6}$", totp_code):
            return render_template("login_2fa.html", error="Please enter a valid 6-digit code.")

        totp = pyotp.TOTP(user["totp_secret"])
        if not totp.verify(totp_code):
            return render_template("login_2fa.html", error="Invalid code. Please try again.")

        session["login_2fa_pending"] = False
        session["login_2fa_verified"] = True

        if user.get("pin_hash"):
            return redirect(url_for("login.pin"))
        else:
            return redirect(url_for("login.set_pin"))

    return render_template("login_2fa.html")


@login_bp.route("/login/set-pin", methods=["GET", "POST"])
def set_pin():
    if not session.get("login_2fa_verified"):
        return redirect(url_for("login.login"))

    if request.method == "POST":
        pin = request.form.get("pin", "").strip()
        confirm_pin = request.form.get("confirm_pin", "").strip()

        if not re.match(r"^\d{4,6}$", pin):
            return render_template("set_pin.html", error="PIN must be 4 to 6 digits.")

        if pin != confirm_pin:
            return render_template("set_pin.html", error="PINs do not match.")

        pin_hash = bcrypt.hashpw(pin.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")
        update_user_pin(session["login_phone"], pin_hash)

        session["authenticated"] = True
        session["last_activity"] = time.time()
        session["login_2fa_verified"] = False
        return redirect(url_for("login.dashboard"))

    return render_template("set_pin.html")


@login_bp.route("/login/pin", methods=["GET", "POST"])
def pin():
    phone = session.get("login_phone")
    if not phone:
        return redirect(url_for("login.login"))

    # Allow access if 2FA was just verified or if session timed out (PIN re-entry)
    if not session.get("login_2fa_verified") and session.get("authenticated") is not False:
        return redirect(url_for("login.login"))

    user = get_user_by_phone(phone)

    if request.method == "POST":
        pin_input = request.form.get("pin", "").strip()

        if not pin_input:
            return render_template("enter_pin.html", error="Please enter your PIN.")

        if not bcrypt.checkpw(pin_input.encode("utf-8"), user["pin_hash"].encode("utf-8")):
            return render_template("enter_pin.html", error="Invalid PIN.")

        session["authenticated"] = True
        session["last_activity"] = time.time()
        session["login_2fa_verified"] = False
        return redirect(url_for("login.dashboard"))

    return render_template("enter_pin.html")


@login_bp.route("/dashboard")
@require_auth
def dashboard():
    phone = session.get("login_phone")
    return render_template("dashboard.html", phone=phone)


@login_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login.login"))
