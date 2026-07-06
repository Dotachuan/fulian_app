from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.core.config import settings


class WechatMiniappError(Exception):
    pass


@dataclass
class WechatPhoneNumberResult:
    phone_number: str
    pure_phone_number: str
    country_code: str


_token_cache: dict[str, Any] = {
    "value": "",
    "expires_at": 0.0,
}


def _post_json(url: str, payload: dict[str, Any]) -> dict[str, Any]:
    req = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=settings.WECHAT_API_TIMEOUT_SECONDS) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise WechatMiniappError(f"Wechat API HTTP error: {exc.code} {detail}") from exc
    except URLError as exc:
        raise WechatMiniappError(f"Wechat API network error: {exc.reason}") from exc


def _get_json(url: str) -> dict[str, Any]:
    req = Request(url, method="GET")
    try:
        with urlopen(req, timeout=settings.WECHAT_API_TIMEOUT_SECONDS) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise WechatMiniappError(f"Wechat API HTTP error: {exc.code} {detail}") from exc
    except URLError as exc:
        raise WechatMiniappError(f"Wechat API network error: {exc.reason}") from exc


def _ensure_credentials() -> None:
    if settings.WECHAT_MINIAPP_APPID and settings.WECHAT_MINIAPP_SECRET:
        return
    raise WechatMiniappError("Wechat miniapp credentials are not configured.")


def get_access_token() -> str:
    _ensure_credentials()

    now = time.time()
    if _token_cache["value"] and now < float(_token_cache["expires_at"]) - 120:
        return str(_token_cache["value"])

    payload = {
        "grant_type": "client_credential",
        "appid": settings.WECHAT_MINIAPP_APPID,
        "secret": settings.WECHAT_MINIAPP_SECRET,
        "force_refresh": False,
    }
    data = _post_json("https://api.weixin.qq.com/cgi-bin/stable_token", payload)
    access_token = data.get("access_token")
    if not access_token:
        query = urlencode(
            {
                "grant_type": "client_credential",
                "appid": settings.WECHAT_MINIAPP_APPID,
                "secret": settings.WECHAT_MINIAPP_SECRET,
            }
        )
        fallback_url = f"https://api.weixin.qq.com/cgi-bin/token?{query}"
        fallback_data = _get_json(fallback_url)
        access_token = fallback_data.get("access_token")
        if not access_token:
            stable_errmsg = data.get("errmsg", "unknown error")
            stable_errcode = data.get("errcode")
            fallback_errmsg = fallback_data.get("errmsg", "unknown error")
            fallback_errcode = fallback_data.get("errcode")
            raise WechatMiniappError(
                "Failed to get Wechat access token "
                f"(stable_token: {stable_errcode} {stable_errmsg}; "
                f"token: {fallback_errcode} {fallback_errmsg})"
            )
        data = fallback_data

    expires_in = int(data.get("expires_in") or 7200)
    _token_cache["value"] = access_token
    _token_cache["expires_at"] = now + expires_in
    return access_token


def get_phone_number(phone_code: str) -> WechatPhoneNumberResult:
    if not phone_code:
        raise WechatMiniappError("Wechat phone code is required.")

    access_token = get_access_token()
    query = urlencode({"access_token": access_token})
    url = f"https://api.weixin.qq.com/wxa/business/getuserphonenumber?{query}"
    data = _post_json(url, {"code": phone_code})

    if data.get("errcode") not in (0, None):
        raise WechatMiniappError(
            f"Failed to get Wechat phone number: {data.get('errmsg', 'unknown error')}"
        )

    phone_info = data.get("phone_info") or {}
    phone_number = phone_info.get("purePhoneNumber") or phone_info.get("phoneNumber")
    if not phone_number:
        raise WechatMiniappError("Wechat phone number is empty.")

    return WechatPhoneNumberResult(
        phone_number=phone_info.get("phoneNumber") or phone_number,
        pure_phone_number=phone_info.get("purePhoneNumber") or phone_number,
        country_code=phone_info.get("countryCode") or "86",
    )
