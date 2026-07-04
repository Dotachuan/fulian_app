from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class PublicDonationOut(BaseModel):
    donation_no: str
    donor_name: str
    donation_date: date
    amount: Decimal
    target_name: str


class PublicDonationPage(BaseModel):
    items: list[PublicDonationOut]
    total: int


class PublicDonationSummary(BaseModel):
    donor_name: str
    total_count: int
    total_amount: Decimal
    year: Optional[int] = None
    first_year: Optional[int] = None
    current_year: int
    support_years: int = 0


class PublicNewsLinkOut(BaseModel):
    id: int
    title: str
    summary: Optional[str] = None
    source_url: str
    published_at: Optional[date] = None


class PublicParkLinkOut(BaseModel):
    id: int
    title: str
    summary: Optional[str] = None
    image_url: str
    target_url: str
    published_at: Optional[date] = None


class PublicProjectLinkOut(BaseModel):
    id: int
    section_key: str
    title: str
    summary: Optional[str] = None
    image_url: str
    target_url: str
    published_at: Optional[date] = None


class PublicProjectFundOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    total_income: Decimal
    total_expense: Decimal
    balance: Decimal


class PublicProjectSectionOut(BaseModel):
    key: str
    title: str
    summary: str
    total_income: Decimal
    total_expense: Decimal
    balance: Decimal
    funds: list[PublicProjectFundOut]
    links: list[PublicProjectLinkOut]
    news_items: list[PublicNewsLinkOut]


class PublicProjectProgressOut(BaseModel):
    sections: list[PublicProjectSectionOut]


class PublicProjectLinkPage(BaseModel):
    items: list[PublicProjectLinkOut]
    total: int


class PublicIndustrialParkOut(BaseModel):
    title: str
    summary: str
    content: str
    links: list[PublicParkLinkOut]
    news_items: list[PublicNewsLinkOut]
