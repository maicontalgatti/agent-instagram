"""Evita vazar segredos (tokens, SAS, etc.) em prints e logs."""

from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import urlparse, urlunparse

REDACTED = "***REDACTED***"


def _is_sensitive_key(key: str) -> bool:
    k = key.lower()
    needles = (
        "token",
        "secret",
        "password",
        "api_key",
        "apikey",
        "authorization",
        "refresh",
        "credential",
    )
    return any(n in k for n in needles)


def sanitize_text(text: str) -> str:
    if not text:
        return text
    out = re.sub(
        r"(?i)(access_token|client_secret|refresh_token|token|api_key|apikey|sig|signature)=([^&\s\"']+)",
        lambda m: f"{m.group(1)}={REDACTED}",
        text,
    )
    out = re.sub(r"(?i)(bearer\s+)(\S+)", rf"\1{REDACTED}", out)
    return out


def sanitize_json_obj(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: (REDACTED if _is_sensitive_key(k) else sanitize_json_obj(v)) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize_json_obj(x) for x in obj]
    if isinstance(obj, str):
        return sanitize_text(obj)
    return obj


def format_http_body_for_log(body: str) -> str:
    """Resposta HTTP: tenta JSON e mascara chaves sensíveis; senão aplica regex em texto."""
    if not body:
        return ""
    try:
        data = json.loads(body)
        return json.dumps(sanitize_json_obj(data), ensure_ascii=False)
    except (json.JSONDecodeError, TypeError):
        return sanitize_text(body)


def sanitize_url_for_log(url: str | None) -> str:
    """URLs de imagem temporárias (ex.: DALL-E em blob) podem levar SAS/tokens na query."""
    if not url:
        return ""
    p = urlparse(url)
    if p.query or p.fragment:
        base = urlunparse((p.scheme, p.netloc, p.path, p.params, "", ""))
        return f"{base}?{REDACTED}"
    return url


def safe_exc(exc: BaseException) -> str:
    return sanitize_text(str(exc))


def credentials_loaded_hint(instagram_token: str | None, ig_id: str | None) -> str:
    """Confirma carregamento sem exibir valores das variáveis."""
    return (
        f"Instagram: INSTAGRAM_ACCESS_TOKEN={'definido' if instagram_token else 'ausente'}, "
        f"INSTAGRAM_BUSINESS_ACCOUNT_ID={'definido' if ig_id else 'ausente'}"
    )
