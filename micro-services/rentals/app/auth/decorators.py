from functools import wraps
from flask import abort, g, request
from .firebase import verify_token


def _extract_bearer_token() -> str:
    authorization = request.headers.get("Authorization", "")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        abort(401, description="A valid Bearer token is required")
    return token.strip()


def _authenticate_request() -> dict:
    token = _extract_bearer_token()
    try:
        claims = verify_token(token)
    except ValueError as exc:
        abort(401, description=str(exc))
    g.current_user = claims
    return claims


def require_authentication(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        _authenticate_request()
        return view_func(*args, **kwargs)
    return wrapped