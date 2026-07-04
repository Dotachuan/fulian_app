from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, model_validator


class FundBase(BaseModel):
    name: str
    type: str = "sub"
    description: Optional[str] = None
    status: str = "active"
    sort_order: int = 0


class FundCreate(FundBase):
    pass


class FundUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    sort_order: Optional[int] = None


class FundOut(FundBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FundPublicOut(BaseModel):
    id: int
    name: str
    type: str
    description: Optional[str] = None
    balance: Decimal


class PageFund(BaseModel):
    items: list[FundOut]
    total: int


class FundUsageBase(BaseModel):
    fund_id: int
    record_date: date
    project_desc: str
    income_amount: Decimal = Decimal("0")
    expense_amount: Decimal = Decimal("0")
    remark: Optional[str] = None

    @model_validator(mode="after")
    def validate_amounts(self):
        if self.income_amount < 0 or self.expense_amount < 0:
            raise ValueError("amounts cannot be negative")
        if self.income_amount == 0 and self.expense_amount == 0:
            raise ValueError("income or expense amount is required")
        return self


class FundUsageCreate(FundUsageBase):
    pass


class FundUsageUpdate(BaseModel):
    record_date: Optional[date] = None
    project_desc: Optional[str] = None
    income_amount: Optional[Decimal] = None
    expense_amount: Optional[Decimal] = None
    remark: Optional[str] = None


class FundUsageOut(FundUsageBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FundUsagePublicOut(BaseModel):
    record_date: date
    project_desc: str
    income_amount: Decimal
    expense_amount: Decimal


class FundUsageSummary(BaseModel):
    fund_id: int
    fund_name: str
    total_income: Decimal
    total_expense: Decimal
    balance: Decimal
    description: Optional[str] = None


class PageFundUsage(BaseModel):
    items: list[FundUsageOut]
    total: int


class PublicFundUsagePage(BaseModel):
    summary: FundUsageSummary
    items: list[FundUsagePublicOut]
    total: int

