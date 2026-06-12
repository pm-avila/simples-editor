from dataclasses import dataclass
import os
from typing import Mapping, Optional


@dataclass(frozen=True)
class SupabaseAuthConfig:
    url: str
    anon_key: str
    jwt_secret: Optional[str]


def _read_required_env(source, key):
    value = source[key].strip()
    if not value:
        raise ValueError(f"{key} must not be blank")
    return value


def _read_optional_env(source: Mapping[str, str], key: str) -> Optional[str]:
    value = source.get(key)
    if value is None:
        return None
    value = value.strip()
    return value or None


def load_supabase_auth_config(env=None):
    source = os.environ if env is None else env
    return SupabaseAuthConfig(
        url=_read_required_env(source, "SUPABASE_URL"),
        anon_key=_read_required_env(source, "SUPABASE_ANON_KEY"),
        jwt_secret=_read_optional_env(source, "SUPABASE_JWT_SECRET"),
    )


def auth_model_summary():
    return (
        "Supabase v1 uses auth.users as the identity source, and the backend validates "
        "JWT locally (JWKS for asymmetric tokens; shared secret for legacy HS256) "
        "without querying the database."
    )
