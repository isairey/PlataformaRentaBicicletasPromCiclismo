from functools import wraps

from flask import abort, g, request

from .firebase import verify_token


def _extract_bearer_token() -> str:
    authorization = request.headers.get("Authorization", "")
    scheme, _, token = authorization.partition(" ")

    if scheme.lower() != "bearer" or not token.strip():
        abort(401, description="A valid Bearer token is required")

    return token.strip()


def _is_admin(claims: dict) -> bool:
    return claims.get("admin") is True or str(claims.get("role", "")).lower() == "admin"


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


def require_admin(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        claims = _authenticate_request()

        if not _is_admin(claims):
            abort(403, description="Admin privileges are required")

        return view_func(*args, **kwargs)

    return wrapped
