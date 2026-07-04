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


def _normalize_phone(value: str) -> str:
    return re.sub(r"\s+", "", value.strip())


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


class MemberAuthSendCodeIn(BaseModel):
    phone: str

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        phone = _normalize_phone(value)
        if not MOBILE_PHONE_PATTERN.fullmatch(phone):
            raise ValueError("请输入正确的手机号码")
        return phone


class MemberAuthSendCodeOut(BaseModel):
    success: bool = True
    phone: str
    debug_code: Optional[str] = None
    expires_in_seconds: int = 300


class MemberAuthLoginIn(MemberAuthSendCodeIn):
    code: str


class MemberAuthWechatPhoneLoginIn(BaseModel):
    phone_code: str


class MemberPublicOut(BaseModel):
    id: int
    phone: str
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    work_unit: Optional[str] = None
    resident_city: Optional[str] = None
    donor_id: Optional[int] = None
    donor_name: Optional[str] = None
    status: str
    binding_status: str
    binding_source: str = "auto"
    member_level: str = "non_member"
    member_level_label: str = "非会员"
    note: Optional[str] = None
    first_login_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MemberAuthTokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    member: MemberPublicOut


class MemberUpdate(BaseModel):
    phone: Optional[str] = None
    name: Optional[str] = None
    work_unit: Optional[str] = None
    resident_city: Optional[str] = None
    donor_id: Optional[int] = None
    status: Optional[str] = None
    note: Optional[str] = None
    sync_donor_phone: bool = False

    @field_validator("phone")
    @classmethod
    def validate_optional_phone(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        phone = _normalize_phone(value)
        if not MOBILE_PHONE_PATTERN.fullmatch(phone):
            raise ValueError("请输入正确的手机号码")
        return phone


class MemberProfileUpdate(BaseModel):
    name: str
    work_unit: str = ""
    resident_city: str = ""
    phone: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        text = value.strip()
        if not text:
            raise ValueError("姓名不能为空")
        return text

    @field_validator("work_unit", "resident_city")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()

    @field_validator("phone")
    @classmethod
    def validate_profile_phone(cls, value: str) -> str:
        phone = _normalize_phone(value)
        if not MOBILE_PHONE_PATTERN.fullmatch(phone):
            raise ValueError("请输入正确的手机号码")
        return phone


class MemberProfileOut(BaseModel):
    name: str = ""
    avatar_url: str = ""
    work_unit: str = ""
    resident_city: str = ""
    phone: str
    phone_note: str = "电话号码仅用于身份验证，不会在通讯录中公开展示。"


class MemberAvatarFromUrlIn(BaseModel):
    avatar_url: str

    @field_validator("avatar_url")
    @classmethod
    def validate_avatar_url(cls, value: str) -> str:
        url = value.strip()
        if not url:
            raise ValueError("头像地址不能为空")
        if not re.match(r"^https?://", url, re.IGNORECASE):
            raise ValueError("头像地址格式不正确")
        return url


class MemberBindingCodeCreateIn(BaseModel):
    donor_id: int
    expires_in_days: int = 7
    note: Optional[str] = None

    @field_validator("expires_in_days")
    @classmethod
    def validate_days(cls, value: int) -> int:
        if value < 1 or value > 90:
            raise ValueError("绑定码有效期需在 1 到 90 天之间")
        return value


class MemberBindingCodeRedeemIn(BaseModel):
    code: str

    @field_validator("code")
    @classmethod
    def validate_code(cls, value: str) -> str:
        code = value.strip().upper()
        if not code:
            raise ValueError("请输入绑定码")
        return code


class MemberBindingCodeOut(BaseModel):
    id: int
    code: str
    member_id: int
    donor_id: int
    donor_name: Optional[str] = None
    status: str
    note: Optional[str] = None
    expires_at: datetime
    used_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PageMember(BaseModel):
    items: list[MemberPublicOut]
    total: int


class MemberInvoiceProfileBase(BaseModel):
    title: str
    phone: str
    email: str
    identity_no: str
    remark: Optional[str] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        phone = _normalize_phone(value)
        if not (MOBILE_PHONE_PATTERN.fullmatch(phone) or LANDLINE_PHONE_PATTERN.fullmatch(phone)):
            raise ValueError("请输入正确的手机号码或座机号码")
        return phone

    @field_validator("identity_no")
    @classmethod
    def validate_identity_no(cls, value: str) -> str:
        identity_no = value.strip().upper()
        if not _is_valid_identity_no(identity_no):
            raise ValueError("请输入正确的身份证号或统一社会信用代码")
        return identity_no


class MemberInvoiceProfileUpdate(MemberInvoiceProfileBase):
    pass


class MemberInvoiceProfileOut(MemberInvoiceProfileBase):
    pass


class MemberInvoiceRequestCreate(BaseModel):
    donor_name: Optional[str] = None
    amount: Decimal
    donation_date: date
    email: Optional[str] = None
    phone: Optional[str] = None
    identity_no: Optional[str] = None
    remark: Optional[str] = None


class MemberSuggestionCreate(BaseModel):
    contact: str = ""
    content: str

    @field_validator("contact")
    @classmethod
    def strip_contact(cls, value: str) -> str:
        return value.strip()

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        text = value.strip()
        if not text:
            raise ValueError("请输入建议内容")
        if len(text) > 2000:
            raise ValueError("建议内容不能超过 2000 个字")
        return text


class MemberSuggestionOut(BaseModel):
    id: int
    member_name: str = ""
    member_phone: str = ""
    contact: str = ""
    content: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class MemberSuggestionAdminUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        status = value.strip()
        if status not in {"pending", "processed", "rejected"}:
            raise ValueError("状态必须为 pending、processed 或 rejected")
        return status


class MemberSuggestionAdminOut(MemberSuggestionOut):
    member_id: int
    updated_at: Optional[datetime] = None


class PageMemberSuggestion(BaseModel):
    items: list[MemberSuggestionAdminOut]
    total: int


class MemberDirectoryItem(BaseModel):
    id: int
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    work_unit: Optional[str] = None
    resident_city: Optional[str] = None
    member_level: str = "non_member"
    member_level_label: str = "非会员"

    model_config = {"from_attributes": True}


class PageMemberDirectory(BaseModel):
    items: list[MemberDirectoryItem]
    total: int


class MemberDonationItem(BaseModel):
    donation_no: str
    donation_date: date
    amount: Decimal
    target_name: str


class PageMemberDonation(BaseModel):
    items: list[MemberDonationItem]
    total: int


class MemberDonationSummary(BaseModel):
    donor_name: str
    total_count: int
    total_amount: Decimal
    first_year: Optional[int] = None
    current_year: int
    support_years: int = 0


class MemberCertificateOut(BaseModel):
    donor_name: str
    total_amount: Decimal
    current_year_amount: Decimal = Decimal("0")
    total_count: int
    first_year: Optional[int] = None
    current_year: int
    support_years: int = 0
    title: str
    subtitle: str
    message: str
    footer: str
    issued_on: str
