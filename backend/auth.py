import jwt
from functools import wraps


class AuthError(Exception):
    """Raised when backend authentication fails."""


def decode_supabase_jwt(token, jwt_secret):
    try:
        return jwt.decode(token, jwt_secret, algorithms=["HS256"])
    except jwt.PyJWTError as exc:
        raise AuthError("invalid token") from exc


def extract_user_id(claims):
    user_id = claims.get("sub")
    if not user_id:
        raise AuthError("missing sub claim")
    return user_id


def _extract_bearer_token(request):
    header = request.headers.get("Authorization", "")
    prefix = "Bearer "
    if not header.startswith(prefix):
        raise AuthError("missing bearer token")
    token = header[len(prefix):].strip()
    if not token:
        raise AuthError("missing bearer token")
    return token


def verify_jwt(jwt_secret):
    def decorator(handler):
        @wraps(handler)
        def wrapped(request, *args, **kwargs):
            token = _extract_bearer_token(request)
            claims = decode_supabase_jwt(token, jwt_secret)
            request.user_id = extract_user_id(claims)
            return handler(request, *args, **kwargs)

        return wrapped

    return decorator
