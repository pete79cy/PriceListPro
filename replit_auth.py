import hmac
import jwt
import os
import uuid
from functools import wraps
from urllib.parse import urlencode

from flask import Blueprint, flash, g, session, redirect, request, render_template, url_for
from flask_dance.consumer import (
    OAuth2ConsumerBlueprint,
    oauth_authorized,
    oauth_error,
)
from flask_dance.consumer.storage import BaseStorage
from flask_login import LoginManager, login_user, logout_user, current_user
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError
from sqlalchemy.exc import NoResultFound
from werkzeug.local import LocalProxy
from werkzeug.security import check_password_hash

from app import app, db
from models import OAuth, User

login_manager = LoginManager(app)
login_manager.login_view = "replit_auth.login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class UserSessionStorage(BaseStorage):

    def get(self, blueprint):
        try:
            token = db.session.query(OAuth).filter_by(
                user_id=current_user.get_id(),
                browser_session_key=g.browser_session_key,
                provider=blueprint.name,
            ).one().token
        except NoResultFound:
            token = None
        return token

    def set(self, blueprint, token):
        db.session.query(OAuth).filter_by(
            user_id=current_user.get_id(),
            browser_session_key=g.browser_session_key,
            provider=blueprint.name,
        ).delete()
        new_model = OAuth()
        new_model.user_id = current_user.get_id()
        new_model.browser_session_key = g.browser_session_key
        new_model.provider = blueprint.name
        new_model.token = token
        db.session.add(new_model)
        db.session.commit()

    def delete(self, blueprint):
        db.session.query(OAuth).filter_by(
            user_id=current_user.get_id(),
            browser_session_key=g.browser_session_key,
            provider=blueprint.name).delete()
        db.session.commit()


def get_auth_mode():
    configured_mode = (os.environ.get("AUTH_MODE") or "").strip().lower()
    if configured_mode in {"local", "replit"}:
        return configured_mode
    return "replit" if os.environ.get("REPL_ID") else "local"


def is_replit_auth_enabled():
    return get_auth_mode() == "replit"


def ensure_browser_session():
    if "_browser_session_key" not in session:
        session["_browser_session_key"] = uuid.uuid4().hex
    session.modified = True
    g.browser_session_key = session["_browser_session_key"]


def is_truthy(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def ensure_local_user():
    """Ensure the local admin user row exists in the DB and return it.

    This does NOT log the user in — call login_user() separately after
    verifying credentials.
    """
    ensure_browser_session()
    g.flask_dance_replit = None

    user_id = os.environ.get("LOCAL_AUTH_USER_ID", "local-admin")
    user = User.query.get(user_id)

    if user is None:
        user = User(
            id=user_id,
            email=os.environ.get("LOCAL_AUTH_EMAIL", "admin@example.com"),
            first_name=os.environ.get("LOCAL_AUTH_FIRST_NAME", "Local"),
            last_name=os.environ.get("LOCAL_AUTH_LAST_NAME", "Admin"),
            is_admin=is_truthy(os.environ.get("LOCAL_AUTH_IS_ADMIN"), default=True),
        )
        db.session.add(user)
        db.session.commit()
    else:
        updated = False
        desired_email = os.environ.get("LOCAL_AUTH_EMAIL")
        desired_first_name = os.environ.get("LOCAL_AUTH_FIRST_NAME")
        desired_last_name = os.environ.get("LOCAL_AUTH_LAST_NAME")
        desired_admin = os.environ.get("LOCAL_AUTH_IS_ADMIN")

        if desired_email and user.email != desired_email:
            user.email = desired_email
            updated = True
        if desired_first_name and user.first_name != desired_first_name:
            user.first_name = desired_first_name
            updated = True
        if desired_last_name and user.last_name != desired_last_name:
            user.last_name = desired_last_name
            updated = True
        if desired_admin is not None:
            parsed_admin = is_truthy(desired_admin, default=True)
            if user.is_admin != parsed_admin:
                user.is_admin = parsed_admin
                updated = True

        if updated:
            db.session.commit()

    return user


def verify_admin_credentials(username, password):
    """Compare submitted credentials with ADMIN_USERNAME / ADMIN_PASSWORD env vars.

    Accepts either ADMIN_PASSWORD (plain) or ADMIN_PASSWORD_HASH
    (werkzeug.security hashed). Uses constant-time comparison for the plain
    case to avoid timing attacks.
    """
    expected_username = os.environ.get("ADMIN_USERNAME", "admin")
    expected_password = os.environ.get("ADMIN_PASSWORD", "")
    expected_password_hash = os.environ.get("ADMIN_PASSWORD_HASH", "")

    if not expected_password and not expected_password_hash:
        return False

    if not hmac.compare_digest(username or "", expected_username):
        return False

    if expected_password_hash:
        return check_password_hash(expected_password_hash, password or "")

    return hmac.compare_digest(password or "", expected_password)


def make_replit_blueprint():
    if not is_replit_auth_enabled():
        local_bp = Blueprint("replit_auth", __name__)

        @local_bp.before_app_request
        def set_local_session():
            ensure_browser_session()
            g.flask_dance_replit = None

        @local_bp.route("/login", methods=["GET", "POST"])
        def login():
            if current_user.is_authenticated:
                return redirect(url_for("index"))

            if request.method == "POST":
                username = (request.form.get("username") or "").strip()
                password = request.form.get("password") or ""

                if verify_admin_credentials(username, password):
                    user = ensure_local_user()
                    login_user(user, remember=True)
                    next_url = (
                        request.args.get("next")
                        or session.pop("next_url", None)
                        or url_for("index")
                    )
                    return redirect(next_url)

                flash("Invalid username or password.", "danger")
                return render_template("auth_login.html"), 401

            return render_template("auth_login.html")

        @local_bp.route("/logout")
        def logout():
            logout_user()
            session.clear()
            flash("You have been signed out.", "success")
            return redirect(url_for("replit_auth.login"))

        @local_bp.route("/error")
        def error():
            return render_template("403.html"), 403

        @local_bp.route("/access-denied")
        def access_denied():
            return render_template("403.html"), 403

        return local_bp

    try:
        repl_id = os.environ['REPL_ID']
    except KeyError:
        raise SystemExit("the REPL_ID environment variable must be set")

    issuer_url = os.environ.get('ISSUER_URL', "https://replit.com/oidc")

    replit_bp = OAuth2ConsumerBlueprint(
        "replit_auth",
        __name__,
        client_id=repl_id,
        client_secret=None,
        base_url=issuer_url,
        authorization_url_params={
            "prompt": "login consent",
        },
        token_url=issuer_url + "/token",
        token_url_params={
            "auth": (),
            "include_client_id": True,
        },
        auto_refresh_url=issuer_url + "/token",
        auto_refresh_kwargs={
            "client_id": repl_id,
        },
        authorization_url=issuer_url + "/auth",
        use_pkce=True,
        code_challenge_method="S256",
        scope=["openid", "profile", "email", "offline_access"],
        storage=UserSessionStorage(),
    )

    @replit_bp.before_app_request
    def set_applocal_session():
        ensure_browser_session()
        g.flask_dance_replit = replit_bp.session

    @replit_bp.route("/logout")
    def logout():
        del replit_bp.token
        logout_user()

        end_session_endpoint = issuer_url + "/session/end"
        encoded_params = urlencode({
            "client_id":
            repl_id,
            "post_logout_redirect_uri":
            request.url_root,
        })
        logout_url = f"{end_session_endpoint}?{encoded_params}"

        return redirect(logout_url)

    @replit_bp.route("/error")
    def error():
        return render_template("403.html"), 403

    @replit_bp.route("/access-denied")
    def access_denied():
        return render_template("403.html"), 403

    return replit_bp


def save_user(user_claims):
    user_id = user_claims['sub']
    existing_user = User.query.get(user_id)

    if existing_user is None:
        user_count = User.query.count()
        if user_count > 0:
            return None

        new_user = User()
        new_user.id = user_id
        new_user.email = user_claims.get('email')
        new_user.first_name = user_claims.get('first_name')
        new_user.last_name = user_claims.get('last_name')
        new_user.profile_image_url = user_claims.get('profile_image_url')
        new_user.is_admin = True
        db.session.add(new_user)
        db.session.commit()
        return new_user

    existing_user.email = user_claims.get('email')
    existing_user.first_name = user_claims.get('first_name')
    existing_user.last_name = user_claims.get('last_name')
    existing_user.profile_image_url = user_claims.get('profile_image_url')
    db.session.commit()
    return existing_user


@oauth_authorized.connect
def logged_in(blueprint, token):
    user_claims = jwt.decode(token['id_token'],
                             options={"verify_signature": False})
    user = save_user(user_claims)

    if user is None:
        return redirect(url_for('replit_auth.access_denied'))

    login_user(user)
    blueprint.token = token
    next_url = session.pop("next_url", None)
    if next_url is not None:
        return redirect(next_url)


@oauth_error.connect
def handle_error(blueprint, error, error_description=None, error_uri=None):
    return redirect(url_for('replit_auth.error'))


def require_login(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_replit_auth_enabled():
            if not current_user.is_authenticated:
                session["next_url"] = get_next_navigation_url(request)
                return redirect(url_for("replit_auth.login"))
            return f(*args, **kwargs)

        if not current_user.is_authenticated:
            session["next_url"] = get_next_navigation_url(request)
            return redirect(url_for('replit_auth.login'))

        try:
            token_data = replit.token
            expires_in = token_data.get('expires_in', 0) if token_data else 0
        except Exception:
            expires_in = 0

        if expires_in < 0:
            _issuer_url = os.environ.get('ISSUER_URL', "https://replit.com/oidc")
            refresh_token_url = _issuer_url + "/token"
            try:
                token = replit.refresh_token(token_url=refresh_token_url,
                                             client_id=os.environ['REPL_ID'])
            except (InvalidGrantError, Exception):
                session["next_url"] = get_next_navigation_url(request)
                return redirect(url_for('replit_auth.login'))
            replit.token_updater(token)

        return f(*args, **kwargs)

    return decorated_function


def get_next_navigation_url(request):
    is_navigation_url = request.headers.get(
        'Sec-Fetch-Mode') == 'navigate' and request.headers.get(
            'Sec-Fetch-Dest') == 'document'
    if is_navigation_url:
        return request.url
    return request.referrer or request.url


replit = LocalProxy(lambda: getattr(g, "flask_dance_replit", None))
