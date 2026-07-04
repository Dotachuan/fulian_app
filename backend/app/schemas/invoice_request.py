from datetime import date, datetime
from decimal import Decimal
import re
from typing import Optional

from pydantic import BaseModel, field_validator


MOBILE_PHONE_PATTERN = re.compile(r"^1[3-9]\d{9}$")
LANDLINE_PHONE_PATTERN = re.compile(r"^0\d{2,3}-?\d{7,8}$")
SOCIAL_CREDIT_CODE_PATTERN = re.compile(r"^[0-9A-HJ-NPQRTUWXY]{18}$")
ID_CARD_WEIGHT_FACTORS = (7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2)
ID_CARD_CHECK_CODES = ("1", "0", "X", "9", "8", "7", "6", "5", "4", "3", "2")


def _is_valid_id_card(value: str) -> bool:
    identity_no = value.strip().upper()
    if not re.fullmatch(r"\d{17}[\dX]", identity_no):
        return False

    try:
        birthday = date(
            int(identity_no[6:10]),
            int(identity_no[10:12]),
            int(identity_no[12:14]),
        )
    except ValueError:
        return False

    if birthday > date.today():
        return False

    checksum = sum(int(identity_no[index]) * factor for index, factor in enumerate(ID_CARD_WEIGHT_FACTORS))
    return ID_CARD_CHECK_CODES[checksum % 11] == identity_no[-1]


def _is_valid_identity_no(value: str) -> bool:
    identity_no = value.strip().upper()
    return _is_valid_id_card(identity_no) or bool(SOCIAL_CREDIT_CODE_PATTERN.fullmatch(identity_no))


class InvoiceRequestCreate(BaseModel):
    donor_name: str
    amount: Decimal
    donation_date: date
    email: str
    phone: str
    identity_no: str
    remark: Optional[str] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        phone = re.sub(r"\s+", "", value.strip())
        if not phone:
            raise ValueError("请输入联系电话")
        if not (MOBILE_PHONE_PATTERN.fullmatch(phone) or LANDLINE_PHONE_PATTERN.fullmatch(phone)):
            raise ValueError("请输入正确的手机号或座机号")
        return phone

    @field_validator("identity_no")
    @classmethod
    def validate_identity_no(cls, value: str) -> str:
        identity_no = value.strip().upper()
        if not identity_no:
            raise ValueError("请输入身份证号或统一社会信用代码")
        if not _is_valid_identity_no(identity_no):
            raise ValueError("请输入正确的身份证号或统一社会信用代码")
        return identity_no


class InvoiceRequestUpdate(BaseModel):
    status: Optional[str] = None
    remark: Optional[str] = None


class InvoiceRequestBatchUpdate(BaseModel):
    ids: list[int]
    status: str
    remark: Optional[str] = None


class InvoiceRequestOut(BaseModel):
    id: int
    request_no: str
    donor_name: str
    amount: Decimal
    donation_date: date
    email: str
    phone: str
    identity_no: str
    remark: Optional[str] = None
    status: str
    processed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class InvoiceRequestPublicOut(BaseModel):
    id: int
    request_no: str
    status: str
    created_at: datetime


class PageInvoiceRequest(BaseModel):
    items: list[InvoiceRequestOut]
    total: int
