import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1 import auth, donations, donors, export, funds, imports, invoice_requests, logs, member, member_auth, members, news, notices, park_links, project_links, public, site_contents, stats, targets, uploads, users
from app.core.config import settings
from app.db import init_db
from app.db.database import engine

app = FastAPI(
    title="Foundation Donation Management System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

prefix = "/api/v1"
app.include_router(auth.router, prefix=prefix, tags=["auth"])
app.include_router(member_auth.router, prefix=prefix, tags=["member_auth"])
app.include_router(users.router, prefix=prefix, tags=["users"])
app.include_router(members.router, prefix=prefix, tags=["members"])
app.include_router(public.router, prefix=prefix, tags=["public"])
app.include_router(member.router, prefix=prefix, tags=["member"])
# Register the static export path before the parameterized donation detail route.
app.include_router(export.router, prefix=prefix, tags=["export"])
app.include_router(invoice_requests.router, prefix=prefix, tags=["invoice_requests"])
app.include_router(imports.router, prefix=prefix, tags=["imports"])
app.include_router(news.router, prefix=prefix, tags=["news"])
app.include_router(notices.router, prefix=prefix, tags=["notices"])
app.include_router(uploads.router, prefix=prefix, tags=["uploads"])
app.include_router(park_links.router, prefix=prefix, tags=["park_links"])
app.include_router(project_links.router, prefix=prefix, tags=["project_links"])
app.include_router(site_contents.router, prefix=prefix, tags=["site_contents"])
app.include_router(donations.router, prefix=prefix, tags=["donations"])
app.include_router(donors.router, prefix=prefix, tags=["donors"])
app.include_router(targets.router, prefix=prefix, tags=["targets"])
app.include_router(funds.router, prefix=prefix, tags=["funds"])
app.include_router(stats.router, prefix=prefix, tags=["stats"])
app.include_router(logs.router, prefix=prefix, tags=["logs"])


@app.on_event("startup")
async def startup():
    init_db.init(engine)


@app.get("/health")
def health():
    return {"status": "ok"}
