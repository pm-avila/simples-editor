import json
import urllib.request

import jwt
from functools import wraps


class AuthError(Exception):
    """Raised when backend authentication fails."""


_jwks_cache: dict[str, object] = {}


def _fetch_ec_public_key(supabase_url: str, kid: str):
    """Fetch and cache EC public key from Supabase JWKS endpoint."""
    cache_key = f"{supabase_url}#{kid}"
    if cache_key in _jwks_cache:
        return _jwks_cache[cache_key]

    jwks_uri = supabase_url.rstrip("/") + "/auth/v1/.well-known/jwks.json"
    try:
        with urllib.request.urlopen(jwks_uri, timeout=5) as resp:
            jwks = json.loads(resp.read())
    except Exception as exc:
        raise AuthError("failed to fetch JWKS") from exc

    from jwt.algorithms import ECAlgorithm  # requires cryptography package
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            pub_key = ECAlgorithm.from_jwk(json.dumps(key))
            _jwks_cache[cache_key] = pub_key
            return pub_key

    raise AuthError(f"no key with kid={kid} in JWKS")


def decode_supabase_jwt(token, jwt_secret, supabase_url=None):
    try:
        header = jwt.get_unverified_header(token)
    except jwt.PyJWTError as exc:
        raise AuthError("invalid token") from exc

    alg = header.get("alg", "HS256")

    if alg == "ES256":
        if not supabase_url:
            raise AuthError("ES256 token but supabase_url not provided")
        kid = header.get("kid")
        pub_key = _fetch_ec_public_key(supabase_url, kid)
        try:
            return jwt.decode(token, pub_key, algorithms=["ES256"])
        except jwt.PyJWTError as exc:
            raise AuthError("invalid token") from exc

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
