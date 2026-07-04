from sqlalchemy import Engine, inspect, text

from app.core.security import hash_password
from app.db.database import Base

# Import all models to ensure metadata registration.
from app.models import attachment, donation, donor, fund, invoice_request, log, member, member_suggestion, news, notice, park_link, project_link, site_content, target, user  # noqa


def init(engine: Engine):
    Base.metadata.create_all(bind=engine)
    _ensure_member_columns(engine)
    _ensure_donor_columns(engine)
    _seed_admin(engine)
    _seed_site_content(engine)


def _ensure_member_columns(engine: Engine):
    inspector = inspect(engine)
    if "members" not in inspector.get_table_names():
        return

    member_columns = {column["name"] for column in inspector.get_columns("members")}
    with engine.begin() as conn:
        if "avatar_url" not in member_columns:
            conn.execute(text("ALTER TABLE members ADD COLUMN avatar_url VARCHAR(1000) NULL"))
        if "resident_city" not in member_columns:
            conn.execute(text("ALTER TABLE members ADD COLUMN resident_city VARCHAR(128) NULL"))
        if "binding_source" not in member_columns:
            conn.execute(text("ALTER TABLE members ADD COLUMN binding_source VARCHAR(20) NOT NULL DEFAULT 'auto'"))


def _ensure_donor_columns(engine: Engine):
    inspector = inspect(engine)
    if "donors" not in inspector.get_table_names():
        return

    donor_columns = {column["name"] for column in inspector.get_columns("donors")}
    with engine.begin() as conn:
        if "binding_code" not in donor_columns:
            conn.execute(text("ALTER TABLE donors ADD COLUMN binding_code VARCHAR(32) NULL"))
            conn.execute(text("CREATE UNIQUE INDEX ix_donors_binding_code ON donors (binding_code)"))
        if "binding_code_status" not in donor_columns:
            conn.execute(text("ALTER TABLE donors ADD COLUMN binding_code_status VARCHAR(20) NULL"))
        if "binding_bound_member_id" not in donor_columns:
            conn.execute(text("ALTER TABLE donors ADD COLUMN binding_bound_member_id INTEGER NULL"))
            conn.execute(text("CREATE INDEX ix_donors_binding_bound_member_id ON donors (binding_bound_member_id)"))
        if "binding_bound_at" not in donor_columns:
            conn.execute(text("ALTER TABLE donors ADD COLUMN binding_bound_at DATETIME NULL"))


def _seed_admin(engine: Engine):
    from sqlalchemy.orm import Session

    from app.models.user import User

    with Session(engine) as db:
        exists = db.query(User).filter_by(username="admin").first()
        if not exists:
            admin = User(
                username="admin",
                password=hash_password("Admin@123"),
                role="admin",
                status="active",
            )
            db.add(admin)
            db.commit()


def _seed_site_content(engine: Engine):
    from sqlalchemy.orm import Session

    from app.models.site_content import SiteContent

    defaults = {
        "mission": {
            "title": "使命",
            "summary": "通过长期公益投入支持教育发展。",
            "content": "请在后台填写福莲教育促进会的使命说明。",
        },
        "vision": {
            "title": "愿景",
            "summary": "连接更多力量，形成可持续的教育公益支持网络。",
            "content": "请在后台填写福莲教育促进会的愿景说明。",
        },
        "about": {
            "title": "机构简介",
            "summary": "福莲教育促进会简介。",
            "content": "请在后台填写机构简介。",
        },
        "contact": {
            "title": "联系我们",
            "summary": "用于展示联系人、联系电话、联系地址、联系邮箱与公众号等信息。",
            "content": "联系人：\n联系电话：\n联系地址：\n联系邮箱：\n公众号：",
        },
        "industrial_park": {
            "title": "福莲产业园",
            "summary": "用于展示福莲产业园定位、合作方向与阶段进展。",
            "content": "请在后台填写福莲产业园的详细介绍与相关信息。",
        },
        "project_main_fund": {
            "title": "福莲教育主基金",
            "summary": "集中展示主基金的阶段进展、资金概况与相关新闻。",
            "content": "请在后台填写福莲教育主基金的补充介绍。",
        },
        "project_medical_fund": {
            "title": "福莲医学基金",
            "summary": "展示医学基金的用途、资金情况与资讯动态。",
            "content": "请在后台填写福莲医学基金的补充介绍。",
        },
        "project_public_activity": {
            "title": "福莲公益活动",
            "summary": "展示公益活动与阶段项目的资金情况及相关新闻。",
            "content": "请在后台填写福莲公益活动的补充介绍。",
        },
        "project_special_fund": {
            "title": "专项基金",
            "summary": "展示专项基金的资金简介、使用情况与资讯链接。",
            "content": "请在后台填写专项基金的补充介绍。",
        },
    }
    with Session(engine) as db:
        for key, value in defaults.items():
            exists = db.query(SiteContent).filter_by(key=key).first()
            if not exists:
                db.add(SiteContent(key=key, status="published", **value))
        db.commit()
