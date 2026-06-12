import json
import subprocess
import urllib.request

import jwt
from functools import wraps


class AuthError(Exception):
    """Raised when backend authentication fails."""


_jwks_cache: dict[str, object] = {}


def _fetch_jwks_json(supabase_url: str) -> dict:
    jwks_uri = supabase_url.rstrip("/") + "/auth/v1/.well-known/jwks.json"
    try:
        with urllib.request.urlopen(jwks_uri, timeout=5) as resp:
            return json.loads(resp.read())
    except Exception:
        # Fallback for transient TLS issues seen with urllib in some containers.
        try:
            result = subprocess.run(
                ["curl", "-fsSL", "--max-time", "8", jwks_uri],
                capture_output=True,
                text=True,
                timeout=10,
            )
        except Exception as exc:
            raise AuthError("failed to fetch JWKS") from exc
        if result.returncode != 0:
            raise AuthError("failed to fetch JWKS")
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise AuthError("failed to fetch JWKS") from exc


def _fetch_remote_user_claims(supabase_url: str, token: str, anon_key: str) -> dict:
    user_uri = supabase_url.rstrip("/") + "/auth/v1/user"
    req = urllib.request.Request(
        user_uri,
        headers={
            "Authorization": f"Bearer {token}",
            "apikey": anon_key,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            return json.loads(resp.read())
    except Exception as exc:
        raise AuthError("invalid token") from exc


def _fetch_public_key(supabase_url: str, kid: str):
    """Fetch and cache public key from Supabase JWKS endpoint."""
    cache_key = f"{supabase_url}#{kid}"
    if cache_key in _jwks_cache:
        return _jwks_cache[cache_key]

    jwks = _fetch_jwks_json(supabase_url)

    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            kty = key.get("kty")
            if kty == "EC":
                from jwt.algorithms import ECAlgorithm  # requires cryptography package
                pub_key = ECAlgorithm.from_jwk(json.dumps(key))
            elif kty == "RSA":
                from jwt.algorithms import RSAAlgorithm  # requires cryptography package
                pub_key = RSAAlgorithm.from_jwk(json.dumps(key))
            else:
                raise AuthError(f"unsupported JWKS key type: {kty}")
            _jwks_cache[cache_key] = pub_key
            return pub_key

    raise AuthError(f"no key with kid={kid} in JWKS")


_JWT_DECODE_OPTIONS = {"verify_aud": False}


def decode_supabase_jwt(token, jwt_secret=None, supabase_url=None, supabase_anon_key=None):
    try:
        header = jwt.get_unverified_header(token)
    except jwt.PyJWTError as exc:
        raise AuthError("invalid token") from exc

    alg = header.get("alg", "HS256")

    if alg in {"ES256", "RS256"}:
        if not supabase_url:
            raise AuthError(f"{alg} token but supabase_url not provided")
        kid = header.get("kid")
        if not kid:
            raise AuthError(f"{alg} token missing kid")
        pub_key = _fetch_public_key(supabase_url, kid)
        try:
            return jwt.decode(token, pub_key, algorithms=[alg], options=_JWT_DECODE_OPTIONS)
        except jwt.PyJWTError as exc:
            raise AuthError("invalid token") from exc

    if alg == "HS256" and not jwt_secret:
        if supabase_url and supabase_anon_key:
            return _fetch_remote_user_claims(supabase_url, token, supabase_anon_key)

    if not jwt_secret:
        raise AuthError("HS256 token but SUPABASE_JWT_SECRET not configured")
    try:
        return jwt.decode(token, jwt_secret, algorithms=["HS256"], options=_JWT_DECODE_OPTIONS)
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
