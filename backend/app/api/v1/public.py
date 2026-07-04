from datetime import date
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.v1.uploads import normalize_public_asset_url
from app.core.deps import get_db
from app.crud import fund as crud_fund, invoice_request as crud_invoice
from app.crud import news as crud_news
from app.crud import notice as crud_notice
from app.crud import park_link as crud_park_link
from app.crud import project_link as crud_project_link
from app.crud import site_content as crud_site_content
from app.models.donation import Donation
from app.models.donor import Donor
from app.models.target import Target
from app.schemas.fund import FundPublicOut, PublicFundUsagePage
from app.schemas.invoice_request import InvoiceRequestCreate, InvoiceRequestPublicOut
from app.schemas.news import NewsPostPublicOut
from app.schemas.notice import NoticePublicOut
from app.schemas.public import (
    PublicDonationPage,
    PublicDonationSummary,
    PublicIndustrialParkOut,
    PublicNewsLinkOut,
    PublicParkLinkOut,
    PublicProjectFundOut,
    PublicProjectLinkOut,
    PublicProjectLinkPage,
    PublicProjectProgressOut,
    PublicProjectSectionOut,
)
from app.schemas.site_content import SiteContentPublicOut

router = APIRouter()

INDUSTRIAL_PARK_INTRO = """2024年5月2日，连城县人民政府、华勤技术股份有限公司、福莲教育促进会三方合作备忘录签订仪式举行，共同建设“福莲产业园”。华勤技术股份有限公司董事长邱文生，福莲教育促进会会长罗培新，福莲教育促进会秘书长吴菲、苏州高新区经发委副主任詹国辉、芜湖立德智兴半导体有限公司首席技术官李元雄，连城县领导蔡东阳、陈聚水、李霞，县直有关单位负责人，连城兴康成生物技术有限公司、昆山合兴源电子有限公司、广东省明科智能设备有限公司、东莞市数控刀具协会、广东华瑞德精密科技有限公司、福建省致锋精密科技有限公司、鼎泰高科技术股份有限公司、东莞市瑞山硬质合金刀具有限公司、深圳市准银科技有限公司、福建省龙勤智能设备有限公司、福建中成新材料有限公司、东莞市凯华环保新材料有限公司等华勤供应链相关企业负责人参加仪式。

为促进产业发展与公益事业的有效联结，助力福莲教育、医疗公益事业的兴旺长盛，推动连城革命老区高质量发展，连城县人民政府、华勤技术股份有限公司、福莲教育促进会三方达成一致合作意向，建设“福莲产业园”。“福莲产业园”入园企业享受《连城县“一园两区”鼓励投资工业项目优惠办法》及相关产业园追加政策。

2024年以来，连城县深化拓展“三争”行动，实施“135”工作思路，深入开展招商引资提效攻坚行动，乘时借势，不断完善招商引资工作模式，积极探索开展“订单招商”，发挥华勤技术等乡贤“头部企业”的支持引领作用，抢抓住建部对口支援、与中建海峡建立战略合作关系机遇，以订单换投资，促进产业链、供应链企业聚集。"""


def _clean_page_size(page_size: int) -> int:
    return max(1, min(page_size, 50))


def _humanize_fund_description(name: str, description: Optional[str]) -> str:
    if not description:
        return ""
    if "Imported fund mapped from donation target" in description:
        return ""
    if "Imported target from" in description:
        return ""
    return description


def _serialize_news_link(item) -> PublicNewsLinkOut:
    return PublicNewsLinkOut(
        id=item.id,
        title=item.title,
        summary=item.summary,
        source_url=item.source_url,
        published_at=item.published_at,
    )


def _serialize_park_link(item) -> PublicParkLinkOut:
    return PublicParkLinkOut(
        id=item.id,
        title=item.title,
        summary=item.summary,
        image_url=normalize_public_asset_url(item.image_url),
        target_url=item.target_url,
        published_at=item.published_at,
    )


def _serialize_project_link(item) -> PublicProjectLinkOut:
    return PublicProjectLinkOut(
        id=item.id,
        section_key=item.section_key,
        title=item.title,
        summary=item.summary,
        image_url=normalize_public_asset_url(item.image_url),
        target_url=item.target_url,
        published_at=item.published_at,
    )


def _get_latest_news(db: Session, limit: int = 3):
    items, _ = crud_news.get_public_list(db, featured_only=False, page=1, page_size=limit)
    return items


def _get_related_news(db: Session, keywords: list[str], limit: int = 3):
    items = _get_latest_news(db, limit=24)
    matched = []
    for item in items:
        haystack = f"{item.title or ''} {item.summary or ''}"
        if any(keyword in haystack for keyword in keywords):
            matched.append(item)
        if len(matched) >= limit:
            break
    return matched or items[:limit]


def _categorize_fund(name: str) -> str:
    if any(keyword in name for keyword in ["医学", "医药", "医护"]):
        return "medical"
    if any(keyword in name for keyword in ["疫情", "地震", "高考", "凉山", "沙龙", "校庆", "活动"]):
        return "activity"
    if name.startswith("福莲") or any(keyword in name for keyword in ["书香", "文心", "华政", "培田", "主体"]):
        return "main"
    return "special"


def _build_project_sections(db: Session) -> list[PublicProjectSectionOut]:
    definitions = [
        {
            "key": "main",
            "title": "福莲教育主基金",
            "content_key": "project_main_fund",
            "default_summary": "围绕福莲教育主基金的长期投入、年度收支与相关资讯进行集中展示。",
            "keywords": ["福莲", "教育", "奖学", "书香", "文心"],
        },
        {
            "key": "medical",
            "title": "福莲医学基金",
            "content_key": "project_medical_fund",
            "default_summary": "展示福莲医学相关专项基金、收支情况与阶段性动态。",
            "keywords": ["医学", "医疗", "健康"],
        },
        {
            "key": "activity",
            "title": "福莲公益活动",
            "content_key": "project_public_activity",
            "default_summary": "归集公益活动与阶段项目的资金使用情况及相关新闻链接。",
            "keywords": ["公益", "活动", "疫情", "地震", "高考"],
        },
        {
            "key": "special",
            "title": "专项基金",
            "content_key": "project_special_fund",
            "default_summary": "展示专项基金的用途、收支概览与资讯更新。",
            "keywords": ["专项", "基金", "合作"],
        },
    ]

    content_map = {item.key: item for item in crud_site_content.list_public(db)}
    funds, _ = crud_fund.list_funds(db, status="active", page=1, page_size=1000)
    grouped_funds: dict[str, list[PublicProjectFundOut]] = {item["key"]: [] for item in definitions}
    totals_map: dict[str, dict[str, Decimal]] = {
        item["key"]: {"income": Decimal("0"), "expense": Decimal("0"), "balance": Decimal("0")}
        for item in definitions
    }

    for fund in funds:
        group_key = _categorize_fund(fund.name)
        total_income, total_expense, balance = crud_fund.fund_totals(db, fund.id)
        grouped_funds[group_key].append(
            PublicProjectFundOut(
                id=fund.id,
                name=fund.name,
                description=_humanize_fund_description(fund.name, fund.description),
                total_income=total_income,
                total_expense=total_expense,
                balance=balance,
            )
        )
        totals_map[group_key]["income"] += total_income
        totals_map[group_key]["expense"] += total_expense
        totals_map[group_key]["balance"] += balance

    sections: list[PublicProjectSectionOut] = []
    for definition in definitions:
        site_item = content_map.get(definition["content_key"])
        related_news = _get_related_news(db, definition["keywords"], limit=3)
        related_links = crud_project_link.get_public_by_section(db, definition["key"], page_size=6)
        totals = totals_map[definition["key"]]
        sections.append(
            PublicProjectSectionOut(
                key=definition["key"],
                title=definition["title"],
                summary=(site_item.summary if site_item and site_item.summary else None)
                or (site_item.content if site_item and site_item.content else None)
                or definition["default_summary"],
                total_income=totals["income"],
                total_expense=totals["expense"],
                balance=totals["balance"],
                funds=grouped_funds[definition["key"]],
                links=[_serialize_project_link(item) for item in related_links],
                news_items=[_serialize_news_link(item) for item in related_news],
            )
        )
    return sections


@router.get("/public/donations/query", response_model=PublicDonationPage)
def query_donations(
    donor_name: str,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    year: Optional[int] = None,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
):
    if not donor_name.strip():
        raise HTTPException(status_code=400, detail="donor_name is required")

    q = (
        db.query(Donation)
        .join(Donor, Donation.donor_id == Donor.id)
        .join(Target, Donation.target_id == Target.id)
        .filter(Donation.is_deleted == False)
        .filter(Donation.status == "normal")
        .filter(Donor.name.like(f"%{donor_name.strip()}%"))
    )
    if year:
        q = q.filter(Donation.donation_date >= date(year, 1, 1))
        q = q.filter(Donation.donation_date <= date(year, 12, 31))
    if date_from:
        q = q.filter(Donation.donation_date >= date_from)
    if date_to:
        q = q.filter(Donation.donation_date <= date_to)

    page_size = _clean_page_size(page_size)
    total = q.count()
    items = (
        q.order_by(Donation.donation_date.desc(), Donation.id.desc())
        .offset((max(page, 1) - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "items": [
            {
                "donation_no": item.donation_no,
                "donor_name": item.donor.name if item.donor else "",
                "donation_date": item.donation_date,
                "amount": item.amount,
                "target_name": item.target.name if item.target else "",
            }
            for item in items
        ],
        "total": total,
    }


@router.get("/public/donations/summary", response_model=PublicDonationSummary)
def donation_summary(
    donor_name: str,
    year: Optional[int] = None,
    db: Session = Depends(get_db),
):
    if not donor_name.strip():
        raise HTTPException(status_code=400, detail="donor_name is required")

    q = (
        db.query(
            func.count(Donation.id),
            func.coalesce(func.sum(Donation.amount), 0),
            func.min(Donation.donation_date),
        )
        .join(Donor, Donation.donor_id == Donor.id)
        .filter(Donation.is_deleted == False)
        .filter(Donation.status == "normal")
        .filter(Donor.name.like(f"%{donor_name.strip()}%"))
    )
    if year:
        q = q.filter(Donation.donation_date >= date(year, 1, 1))
        q = q.filter(Donation.donation_date <= date(year, 12, 31))

    total_count, total_amount, first_donation_date = q.one()
    current_year = date.today().year
    first_year = first_donation_date.year if first_donation_date else None
    return {
        "donor_name": donor_name.strip(),
        "total_count": total_count,
        "total_amount": Decimal(str(total_amount)),
        "year": year,
        "first_year": first_year,
        "current_year": current_year,
        "support_years": current_year - first_year + 1 if first_year else 0,
    }


@router.get("/public/funds")
def public_funds(db: Session = Depends(get_db)):
    funds, _ = crud_fund.list_funds(db, status="active", page=1, page_size=1000)
    items = []
    for fund in funds:
        _, _, balance = crud_fund.fund_totals(db, fund.id)
        items.append(
            FundPublicOut(
                id=fund.id,
                name=fund.name,
                type=fund.type,
                description=_humanize_fund_description(fund.name, fund.description),
                balance=balance,
            )
        )
    return {"items": items}


@router.get("/public/funds/{fund_id}/usage", response_model=PublicFundUsagePage)
def public_fund_usage(
    fund_id: int,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
):
    fund = crud_fund.get_fund(db, fund_id)
    if not fund or fund.status != "active":
        raise HTTPException(status_code=404, detail="fund not found")

    page_size = _clean_page_size(page_size)
    records, total = crud_fund.list_usage_records(
        db,
        fund_id=fund_id,
        date_from=date_from,
        date_to=date_to,
        page=max(page, 1),
        page_size=page_size,
    )
    total_income, total_expense, balance = crud_fund.fund_totals(db, fund_id)
    return {
        "summary": {
            "fund_id": fund.id,
            "fund_name": fund.name,
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": balance,
            "description": _humanize_fund_description(fund.name, fund.description),
        },
        "items": [
            {
                "record_date": record.record_date,
                "project_desc": record.project_desc,
                "income_amount": record.income_amount,
                "expense_amount": record.expense_amount,
            }
            for record in records
        ],
        "total": total,
    }


@router.get("/public/industrial-park", response_model=PublicIndustrialParkOut)
def public_industrial_park(db: Session = Depends(get_db)):
    site_item = crud_site_content.get_by_key(db, "industrial_park")
    related_news = _get_related_news(db, ["产业园", "合作", "华勤", "招商"], limit=4)
    park_links, _ = crud_park_link.get_public_list(db, featured_only=False, page=1, page_size=12)
    summary = site_item.summary.strip() if site_item and site_item.summary else ""
    content = site_item.content.strip() if site_item and site_item.content else ""
    return {
        "title": site_item.title if site_item else "福莲产业园",
        "summary": summary if len(summary) >= 20 else "聚焦订单招商、产业协作与公益联动，持续展示福莲产业园的发展定位、合作进展与相关资讯。",
        "content": content if len(content) >= 120 else INDUSTRIAL_PARK_INTRO,
        "links": [_serialize_park_link(item) for item in park_links],
        "news_items": [_serialize_news_link(item) for item in related_news],
    }


@router.get("/public/project-progress", response_model=PublicProjectProgressOut)
def public_project_progress(db: Session = Depends(get_db)):
    return {"sections": _build_project_sections(db)}


@router.get("/public/project-links", response_model=PublicProjectLinkPage)
def public_project_links(
    section_key: str,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    page = max(1, page)
    page_size = max(1, min(page_size, 100))
    items, total = crud_project_link.get_list(
        db,
        status="published",
        section_key=section_key,
        page=page,
        page_size=page_size,
    )
    return {
        "items": [_serialize_project_link(item) for item in items],
        "total": total,
    }


@router.post("/public/invoice-requests", response_model=InvoiceRequestPublicOut, status_code=201)
def create_public_invoice_request(
    data: InvoiceRequestCreate,
    db: Session = Depends(get_db),
):
    request = crud_invoice.create_request(db, data)
    return request


@router.get("/public/news")
def public_news(
    limit: int | None = None,
    page: int = 1,
    page_size: int = 6,
    featured_only: bool = False,
    db: Session = Depends(get_db),
):
    if limit is not None:
        page = 1
        page_size = limit
    page = max(1, page)
    page_size = max(1, min(page_size, 24))
    items, total = crud_news.get_public_list(
        db,
        featured_only=featured_only,
        page=page,
        page_size=page_size,
    )
    return {
        "items": [
            NewsPostPublicOut(
                id=item.id,
                title=item.title,
                summary=item.summary,
                cover_url=normalize_public_asset_url(item.cover_url),
                source_url=item.source_url,
                source=item.source,
                published_at=item.published_at,
            )
            for item in items
        ],
        "total": total,
    }


@router.get("/public/news/{news_id}", response_model=NewsPostPublicOut)
def public_news_detail(
    news_id: int,
    db: Session = Depends(get_db),
):
    item = crud_news.get(db, news_id)
    if not item or item.status != "published":
        raise HTTPException(status_code=404, detail="news not found")
    return NewsPostPublicOut(
        id=item.id,
        title=item.title,
        summary=item.summary,
        cover_url=normalize_public_asset_url(item.cover_url),
        source_url=item.source_url,
        source=item.source,
        published_at=item.published_at,
    )


@router.get("/public/notices")
def public_notices(
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
):
    items, total = crud_notice.get_public_list(db, page=page, page_size=max(1, min(page_size, 24)))
    return {
        "items": [NoticePublicOut.model_validate(item) for item in items],
        "total": total,
    }


@router.get("/public/notices/{notice_id}", response_model=NoticePublicOut)
def public_notice_detail(
    notice_id: int,
    db: Session = Depends(get_db),
):
    item = crud_notice.get(db, notice_id)
    if not item or item.status != "published":
        raise HTTPException(status_code=404, detail="notice not found")
    return NoticePublicOut.model_validate(item)


@router.get("/public/site-content", response_model=list[SiteContentPublicOut])
def public_site_content(db: Session = Depends(get_db)):
    return crud_site_content.list_public(db)


@router.get("/public/contact", response_model=SiteContentPublicOut)
def public_contact(db: Session = Depends(get_db)):
    item = crud_site_content.get_by_key(db, "contact")
    if not item or item.status != "published":
        raise HTTPException(status_code=404, detail="contact not found")
    return item
