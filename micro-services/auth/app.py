import datetime
import logging
import os
from pathlib import Path

import firebase_admin
import requests
from dotenv import load_dotenv
from google.auth.exceptions import RefreshError
from firebase_admin import auth, credentials, exceptions
from flask import Flask, jsonify, request
from flask_cors import CORS

load_dotenv(Path(__file__).resolve().parent / ".env")

app = Flask(__name__)
CORS(app)

FIREBASE_WEB_API_KEY = os.getenv("FIREBASE_WEB_API_KEY", "")
AUTH_LOGIN_URL = (
    f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
    if FIREBASE_WEB_API_KEY
    else None
)

logging.basicConfig(filename="events.log", level=logging.INFO)


def get_firebase_credentials():
    private_key = os.getenv("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n")
    certificate_data = {
        "type": os.getenv("FIREBASE_TYPE", "service_account"),
        "project_id": os.getenv("FIREBASE_PROJECT_ID", ""),
        "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID", ""),
        "private_key": private_key,
        "client_email": os.getenv("FIREBASE_CLIENT_EMAIL", ""),
        "client_id": os.getenv("FIREBASE_CLIENT_ID", ""),
        "auth_uri": os.getenv(
            "FIREBASE_AUTH_URI",
            "https://accounts.google.com/o/oauth2/auth",
        ),
        "token_uri": os.getenv(
            "FIREBASE_TOKEN_URI",
            "https://oauth2.googleapis.com/token",
        ),
        "auth_provider_x509_cert_url": os.getenv(
            "FIREBASE_AUTH_PROVIDER_X509_CERT_URL",
            "https://www.googleapis.com/oauth2/v1/certs",
        ),
        "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL", ""),
        "universe_domain": os.getenv("FIREBASE_UNIVERSE_DOMAIN", "googleapis.com"),
    }

    required_fields = [
        "project_id",
        "private_key_id",
        "private_key",
        "client_email",
        "client_id",
        "client_x509_cert_url",
    ]
    missing_fields = [field for field in required_fields if not certificate_data[field]]
    if missing_fields:
        raise ValueError(
            "Missing Firebase environment variables: "
            + ", ".join(f"FIREBASE_{field.upper()}" for field in missing_fields)
        )

    return credentials.Certificate(certificate_data)


def initialize_firebase():
    if firebase_admin._apps:
        return
    cred = get_firebase_credentials()
    firebase_admin.initialize_app(cred)


def firebase_configuration_error_response(exc):
    message = str(exc)
    normalized = message.lower()

    if "invalid jwt signature" in normalized:
        detail = (
            "Firebase service account credentials are invalid. "
            "Update the Firebase credentials in the .env file and restart the service."
        )
    elif "token_uri" in normalized or "private key" in normalized:
        detail = (
            "Firebase service account environment variables are malformed or incomplete. "
            "Verify the .env values and replace them with a valid key from Firebase Console."
        )
    else:
        detail = (
            "Firebase credentials could not be used. "
            "Verify the configured Firebase .env values and project configuration."
        )

    return (
        jsonify(
            {
                "error": "FIREBASE_CONFIGURATION_ERROR",
                "message": detail,
            }
        ),
        500,
    )


def log_event(event_type, uid, email, success, details=""):
    timestamp = datetime.datetime.utcnow().isoformat()
    message = f"[{timestamp}] {event_type} - UID: {uid} - Email: {email} - Success: {success} - {details}"
    logging.info(message)


initialize_firebase()


@app.get("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "firebaseConfigured": bool(FIREBASE_WEB_API_KEY),
        }
    )


@app.route("/api/v1/auth/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")
    name = data.get("name") or data.get("Name")
    role = data.get("role") or data.get("rol") or "user"

    errors = []
    if not email or "@" not in email:
        errors.append("Invalid email format")
    if not password or len(password) < 8:
        errors.append("Password must be at least 8 chars")
    if not name:
        errors.append("Name is required")

    if errors:
        return jsonify({"error": "VALIDATION_ERROR", "details": errors}), 400

    try:
        user_record = auth.create_user(
            email=email,
            password=password,
            display_name=name,
            disabled=False,
        )
        auth.set_custom_user_claims(
            user_record.uid,
            {
                "role": role,
                "admin": str(role).lower() == "admin",
            },
        )

        log_event("REGISTER", user_record.uid, email, True)

        return (
            jsonify(
                {
                    "uid": user_record.uid,
                    "email": user_record.email,
                    "createdAt": datetime.datetime.utcnow().isoformat(),
                }
            ),
            201,
        )

    except auth.EmailAlreadyExistsError:
        return jsonify({"error": "EMAIL_ALREADY_EXISTS", "message": "Email already registered"}), 409
    except (RefreshError, ValueError) as exc:
        return firebase_configuration_error_response(exc)
    except exceptions.FirebaseError as exc:
        if "WEAK_PASSWORD" in str(exc):
            return jsonify({"error": "WEAK_PASSWORD", "message": "The password is too weak"}), 400
        return jsonify({"error": "INTERNAL_ERROR", "message": str(exc)}), 500


@app.route("/api/v1/auth/login", methods=["POST"])
def login():
    if not AUTH_LOGIN_URL:
        return jsonify({"error": "CONFIGURATION_ERROR", "message": "FIREBASE_WEB_API_KEY is not configured"}), 500

    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "VALIDATION_ERROR", "details": ["Email and password required"]}), 400

    payload = {"email": email, "password": password, "returnSecureToken": True}
    response = requests.post(AUTH_LOGIN_URL, json=payload, timeout=30)
    res_data = response.json()

    if response.status_code != 200:
        error_msg = res_data.get("error", {}).get("message", "")

        if error_msg == "INVALID_PASSWORD":
            return jsonify({"error": "INVALID_CREDENTIALS", "message": "Wrong password"}), 401
        if error_msg == "EMAIL_NOT_FOUND":
            return jsonify({"error": "USER_NOT_FOUND", "message": "User not registered"}), 404
        if error_msg == "USER_DISABLED":
            return jsonify({"error": "USER_DISABLED", "message": "Account is disabled"}), 403

        return jsonify({"error": "AUTH_ERROR", "message": error_msg}), 400

    log_event("LOGIN", res_data["localId"], email, True)

    return (
        jsonify(
            {
                "idToken": res_data["idToken"],
                "refreshToken": res_data["refreshToken"],
                "expiresIn": int(res_data["expiresIn"]),
            }
        ),
        200,
    )


@app.route("/api/v1/auth/logout", methods=["POST"])
def logout():
    auth_header = request.headers.get("Authorization")
    uid = None

    if auth_header and auth_header.startswith("Bearer "):
        try:
            id_token = auth_header.split(" ", 1)[1]
            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token["uid"]
        except Exception:
            return jsonify({"error": "UNAUTHORIZED", "message": "Invalid or expired token"}), 401

    if not uid:
        return jsonify({"error": "UNAUTHORIZED", "message": "A valid Bearer token is required"}), 401

    try:
        auth.revoke_refresh_tokens(uid)
        log_event("LOGOUT", uid, "N/A", True, "Tokens revoked")
        return jsonify({"message": "Session revoked successfully"}), 200

    except auth.UserNotFoundError:
        return jsonify({"error": "USER_NOT_FOUND", "message": "UID does not exist"}), 404
    except (RefreshError, ValueError) as exc:
        return firebase_configuration_error_response(exc)
    except Exception as exc:
        return jsonify({"error": "INTERNAL_ERROR", "message": str(exc)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
