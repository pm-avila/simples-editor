from backend.auth import AuthError
from backend.auth import decode_supabase_jwt
from backend.auth import extract_user_id


class HandshakeAuthError(Exception):
    """Raised when WebSocket handshake authentication fails."""


def _get_header(headers, name):
    if name in headers:
        return headers[name]
    lowered = name.lower()
    for key, value in headers.items():
        if isinstance(key, str) and key.lower() == lowered:
            return value
    return ""


def _extract_token_from_subprotocol(headers):
    raw = _get_header(headers, "Sec-WebSocket-Protocol")
    if not raw:
        return None

    parts = [part.strip() for part in str(raw).split(",") if part.strip()]
    for part in parts:
        lower = part.lower()
        if lower.startswith("bearer."):
            token = part[7:].strip()
            if token:
                return token
    return None


def _extract_token_from_query(query_args):
    if hasattr(query_args, "getlist"):
        values = query_args.getlist("token")
        for value in values:
            token = str(value).strip()
            if token:
                return token

    value = query_args.get("token") if hasattr(query_args, "get") else None
    if isinstance(value, (list, tuple)):
        for item in value:
            token = str(item).strip()
            if token:
                return token
        return None
    if value is None:
        return None
    token = str(value).strip()
    return token or None


def extract_token_from_handshake(headers, query_args):
    token = _extract_token_from_subprotocol(headers)
    if token:
        return token

    token = _extract_token_from_query(query_args)
    if token:
        return token

    raise HandshakeAuthError("missing bearer token")


def authenticate_ws_handshake(headers, query_args, jwt_secret):
    token = extract_token_from_handshake(headers, query_args)
    try:
        claims = decode_supabase_jwt(token, jwt_secret)
        return extract_user_id(claims)
    except AuthError as exc:
        raise HandshakeAuthError("invalid token") from exc
