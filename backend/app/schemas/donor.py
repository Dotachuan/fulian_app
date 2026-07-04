from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DonorBase(BaseModel):
    name: str
    type: str = "person"
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    id_no: Optional[str] = None
    remark: Optional[str] = None


class DonorCreate(DonorBase):
    pass


class DonorUpdate(DonorBase):
    name: Optional[str] = None


class DonorOut(DonorBase):
    id: int
    binding_code: Optional[str] = None
    binding_code_status: Optional[str] = None
    binding_bound_member_id: Optional[int] = None
    binding_bound_member_name: Optional[str] = None
    binding_bound_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PageDonor(BaseModel):
    items: list[DonorOut]
    total: int


class DonorBindingCodeBatchGenerateIn(BaseModel):
    only_missing: bool = True


class DonorBindingCodeBatchGenerateOut(BaseModel):
    generated_count: int
    reused_count: int
    total_count: int
