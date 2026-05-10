import jwt


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
