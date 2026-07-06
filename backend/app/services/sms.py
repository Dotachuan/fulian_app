from __future__ import annotations

import json
from dataclasses import dataclass

from app.core.config import settings


class SmsProviderError(Exception):
    pass


@dataclass
class SmsSendResult:
    provider: str
    request_id: str = ""
    biz_id: str = ""


def _provider() -> str:
    return (settings.MEMBER_SMS_PROVIDER or "").strip().lower()


def sms_provider_configured() -> bool:
    provider = _provider()
    if provider == "aliyun":
        return all(
            [
                settings.MEMBER_SMS_SIGN_NAME,
                settings.MEMBER_SMS_TEMPLATE_CODE,
                settings.MEMBER_SMS_ACCESS_KEY_ID,
                settings.MEMBER_SMS_ACCESS_KEY_SECRET,
            ]
        )
    return False


def send_member_login_code(phone: str, code: str) -> SmsSendResult:
    provider = _provider()
    if provider == "aliyun":
        return _send_via_aliyun(phone, code)
    raise SmsProviderError("SMS provider is not configured.")


def _send_via_aliyun(phone: str, code: str) -> SmsSendResult:
    try:
        from alibabacloud_dysmsapi20170525.client import Client as DysmsapiClient
        from alibabacloud_dysmsapi20170525 import models as dysmsapi_models
        from alibabacloud_tea_openapi import models as open_api_models
        from alibabacloud_tea_util import models as util_models
    except Exception as exc:  # pragma: no cover - depends on optional sdk install
        raise SmsProviderError(
            "Aliyun SMS SDK is not installed. Please install backend requirements again."
        ) from exc

    config = open_api_models.Config(
        access_key_id=settings.MEMBER_SMS_ACCESS_KEY_ID,
        access_key_secret=settings.MEMBER_SMS_ACCESS_KEY_SECRET,
        endpoint="dysmsapi.aliyuncs.com",
    )
    client = DysmsapiClient(config)
    template_param = json.dumps(
        {settings.MEMBER_SMS_TEMPLATE_PARAM_NAME or "code": code},
        ensure_ascii=False,
        separators=(",", ":"),
    )
    request = dysmsapi_models.SendSmsRequest(
        phone_numbers=phone,
        sign_name=settings.MEMBER_SMS_SIGN_NAME,
        template_code=settings.MEMBER_SMS_TEMPLATE_CODE,
        template_param=template_param,
    )
    runtime = util_models.RuntimeOptions(
        read_timeout=settings.MEMBER_SMS_API_TIMEOUT_SECONDS * 1000,
        connect_timeout=settings.MEMBER_SMS_API_TIMEOUT_SECONDS * 1000,
    )

    try:
        response = client.send_sms_with_options(request, runtime)
    except Exception as exc:  # pragma: no cover - provider/network dependent
        raise SmsProviderError(f"Aliyun SMS request failed: {exc}") from exc

    body = getattr(response, "body", None)
    if not body:
        raise SmsProviderError("Aliyun SMS response body is empty.")

    status_code = getattr(body, "code", "") or ""
    if status_code != "OK":
        message = getattr(body, "message", "") or "unknown error"
        request_id = getattr(body, "request_id", "") or ""
        raise SmsProviderError(f"Aliyun SMS send failed: {status_code} {message} {request_id}".strip())

    return SmsSendResult(
        provider="aliyun",
        request_id=getattr(body, "request_id", "") or "",
        biz_id=getattr(body, "biz_id", "") or "",
    )
