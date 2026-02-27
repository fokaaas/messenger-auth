import time
from functools import wraps

from flask import session, redirect, url_for

from app.config import PIN_LOCK_TIMEOUT


def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("authenticated"):
            return redirect(url_for("login.login"))

        last_activity = session.get("last_activity")
        if last_activity and (time.time() - last_activity > PIN_LOCK_TIMEOUT):
            session["authenticated"] = False
            return redirect(url_for("login.pin"))

        session["last_activity"] = time.time()
        return f(*args, **kwargs)

    return decorated_function
