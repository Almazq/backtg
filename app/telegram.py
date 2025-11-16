import hashlib
import hmac
import json
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple
from urllib.parse import parse_qsl


@dataclass
class VerifiedInitData:
    ok: bool
    reason: Optional[str]
    query_id: Optional[str]
    auth_date: Optional[int]
    user: Optional[Dict[str, Any]]
    raw: Dict[str, str]


def _build_data_check_string(params: Dict[str, str]) -> str:
    """
    Builds the data_check_string according to Telegram docs:
    - Exclude 'hash'
    - Sort by keys alphabetically
    - Join as 'key=value' with '\n'
    Values must be taken exactly as received (already URL-decoded by parse_qsl).
    """
    pairs = [f"{k}={v}" for k, v in params.items() if k != "hash"]
    pairs.sort(key=lambda x: x.split("=", 1)[0])
    return "\n".join(pairs)


def _extract_json(value: Optional[str]) -> Optional[Dict[str, Any]]:
    if not value:
        return None
    try:
        return json.loads(value)
    except Exception:
        return None


def _parse_init_data(init_data: str) -> Tuple[Dict[str, str], Optional[str]]:
    """
    Parses the raw init_data query string into a dict.
    Returns (params_without_duplicates, hash_value).
    """
    # parse_qsl preserves order and URL-decodes values
    items = parse_qsl(init_data, keep_blank_values=True, strict_parsing=False)
    params: Dict[str, str] = {}
    hash_value: Optional[str] = None
    for k, v in items:
        if k == "hash":
            hash_value = v
        else:
            params[k] = v
    return params, hash_value


def verify_init_data(init_data: str, bot_token: str) -> VerifiedInitData:
    """
    Verifies Telegram WebApp initData.
    Algorithm (per Telegram docs):
      - Build data_check_string from all fields except 'hash'
      - secret_key = sha256(bot_token)
      - computed_hash = HMAC_SHA256(data_check_string, secret_key).hexdigest()
      - Compare to provided 'hash' (constant-time)
    """
    params, provided_hash = _parse_init_data(init_data)

    if not provided_hash:
        return VerifiedInitData(
            ok=False,
            reason="Missing 'hash' parameter in init_data",
            query_id=params.get("query_id"),
            auth_date=int(params["auth_date"]) if params.get("auth_date", "").isdigit() else None,
            user=_extract_json(params.get("user")),
            raw=params,
        )

    data_check_string = _build_data_check_string(params)
    secret_key = hashlib.sha256(bot_token.encode("utf-8")).digest()
    computed_hash = hmac.new(secret_key, data_check_string.encode("utf-8"), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(computed_hash, provided_hash):
        return VerifiedInitData(
            ok=False,
            reason="Invalid hash",
            query_id=params.get("query_id"),
            auth_date=int(params["auth_date"]) if params.get("auth_date", "").isdigit() else None,
            user=_extract_json(params.get("user")),
            raw=params,
        )

    return VerifiedInitData(
        ok=True,
        reason=None,
        query_id=params.get("query_id"),
        auth_date=int(params["auth_date"]) if params.get("auth_date", "").isdigit() else None,
        user=_extract_json(params.get("user")),
        raw=params,
    )


