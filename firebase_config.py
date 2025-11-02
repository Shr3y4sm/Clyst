# Firebase Authentication Configuration
import firebase_admin
from firebase_admin import credentials, auth
import os
import requests

# Firebase Web SDK config (for frontend)
FIREBASE_WEB_CONFIG = {
    "apiKey": "AIzaSyCgFUiH7sCILiy7C5RzIfNByr5vQQI1iKw",
    "authDomain": "clyst-2f40e.firebaseapp.com",
    "projectId": "clyst-2f40e",
    "storageBucket": "clyst-2f40e.firebasestorage.app",
    "messagingSenderId": "688738219775",
    "appId": "1:688738219775:web:6ed440ac392d275a927eca"
}

# Initialize Firebase Admin SDK (for backend token verification)
# For development: uses Application Default Credentials or service account key
def init_firebase_admin():
    """Initialize Firebase Admin SDK if not already initialized."""
    if not firebase_admin._apps:
        try:
            # Try to use Application Default Credentials first
            # Or set GOOGLE_APPLICATION_CREDENTIALS env var to your service account JSON path
            firebase_admin.initialize_app()
            print("[OK] Firebase Admin SDK initialized")
        except Exception as e:
            print("[WARNING] Firebase Admin init skipped:", str(e))
            print("Set GOOGLE_APPLICATION_CREDENTIALS to enable server-side token verification")

def verify_firebase_token(id_token):
    """
    Verify a Firebase ID token and return decoded claims.
    Returns None if verification fails.
    """
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        print(f"Token verification via Admin SDK failed: {e}")

    # Fallback: verify using Firebase Identity Toolkit REST API (works without service account)
    try:
        api_key = FIREBASE_WEB_CONFIG.get("apiKey")
        if not api_key:
            raise RuntimeError("Missing Firebase apiKey for REST verification")

        resp = requests.post(
            f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={api_key}",
            json={"idToken": id_token},
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            users = data.get("users", [])
            if users:
                u = users[0]
                # Normalize to look like Admin SDK decoded token keys where possible
                return {
                    "uid": u.get("localId"),
                    "email": u.get("email"),
                    "phone_number": u.get("phoneNumber"),
                    "name": u.get("displayName"),
                    "email_verified": u.get("emailVerified"),
                    "provider_data": u.get("providerUserInfo", []),
                }
        else:
            print(f"REST verification failed: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"Token verification via REST failed: {e}")

    return None


def delete_firebase_user(email: str = None, id_token: str = None):
    """
    Delete a Firebase user using Admin SDK (by email) when available,
    otherwise via Identity Toolkit REST API using the user's ID token.

    Returns (success: bool, message: str)
    """
    # Try Admin SDK deletion by email first when initialized
    try:
        if email and firebase_admin._apps:
            try:
                user_record = auth.get_user_by_email(email)
                auth.delete_user(user_record.uid)
                return True, "Deleted via Admin SDK"
            except firebase_admin.auth.UserNotFoundError:
                return False, "Firebase user not found by email"
            except Exception as e:
                return False, f"Admin SDK deletion failed: {e}"
    except Exception as e:
        # Continue to REST path below
        pass

    # Fallback to REST deletion using idToken
    try:
        if id_token:
            api_key = FIREBASE_WEB_CONFIG.get("apiKey")
            if not api_key:
                return False, "Missing Firebase apiKey for REST deletion"

            resp = requests.post(
                f"https://identitytoolkit.googleapis.com/v1/accounts:delete?key={api_key}",
                json={"idToken": id_token},
                timeout=10,
            )
            if resp.status_code == 200:
                return True, "Deleted via REST API"
            else:
                return False, f"REST deletion failed: {resp.status_code} {resp.text}"
        else:
            return False, "No id_token provided for REST deletion"
    except Exception as e:
        return False, f"REST deletion exception: {e}"

