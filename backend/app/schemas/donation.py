from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel

from app.schemas.donor import DonorOut
from app.schemas.target import TargetOut


class DonationBase(BaseModel):
    donation_date: date
    donor_id: int
    target_id: int
    amount: Decimal
    payment_method: str = "bank"
    receipt_flag: bool = False
    receipt_no: Optional[str] = None
    remark: Optional[str] = None


class DonationCreate(DonationBase):
    pass


class DonationUpdate(BaseModel):
    donation_date: Optional[date] = None
    donor_id: Optional[int] = None
    target_id: Optional[int] = None
    amount: Optional[Decimal] = None
    payment_method: Optional[str] = None
    receipt_flag: Optional[bool] = None
    receipt_no: Optional[str] = None
    remark: Optional[str] = None
    status: Optional[str] = None


class LogItem(BaseModel):
    id: int
    username: Optional[str]
    action: str
    detail: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class DonationOut(DonationBase):
    id: int
    donation_no: str
    status: str
    donor_name: Optional[str] = None
    target_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DonationDetail(DonationOut):
    donor: Optional[DonorOut] = None
    target: Optional[TargetOut] = None
    logs: list[LogItem] = []


class PageDonation(BaseModel):
    items: list[DonationOut]
    total: int
