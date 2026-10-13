from __future__ import annotations

from datetime import date
from decimal import Decimal
import os
from pathlib import Path
import uuid

from PIL import Image, ImageDraw, ImageFont

from app.core.config import settings


CANVAS_WIDTH = 1870
CANVAS_HEIGHT = 1322


def _position(
    left: float,
    top: float,
    size: int,
    max_width: int | None = None,
    weight: str = "500",
    emphasis: bool = False,
) -> dict:
    return {"left": left, "top": top, "size": size, "max_width": max_width, "weight": weight, "emphasis": emphasis}


TEMPLATE_CONFIG = {
    "memberWithCurrent": {
        "file": "member-with-current.jpg",
        "positions": {
            "donorName": _position(28.0, 38.75, 46, 230, "700", True),
            "currentAmount": _position(40.7, 46.45, 35, 250, "700", True),
            "totalAmountWithCurrent": _position(74.4, 46.45, 35, 270, "700", True),
            "supportYears": _position(46.2, 58.9, 34, 90),
            "issuedYear": _position(72.15, 80.95, 31, 92),
            "issuedMonth": _position(77.85, 80.95, 31, 56),
            "issuedDay": _position(81.45, 80.95, 31, 56),
        },
    },
    "memberWithoutCurrent": {
        "file": "member-without-current.jpg",
        "positions": {
            "donorName": _position(28.0, 38.75, 46, 230, "700", True),
            "totalAmountWithoutCurrent": _position(42.6, 46.45, 35, 270, "700", True),
            "supportYears": _position(46.2, 58.9, 34, 90),
            "issuedYear": _position(72.15, 80.95, 31, 92),
            "issuedMonth": _position(77.85, 80.95, 31, 56),
            "issuedDay": _position(81.45, 80.95, 31, 56),
        },
    },
    "directorWithCurrent": {
        "file": "director-with-current.jpg",
        "positions": {
            "donorName": _position(28.0, 38.75, 46, 230, "700", True),
            "currentAmount": _position(42.2, 46.45, 35, 250, "700", True),
            "totalAmountWithCurrent": _position(79.4, 46.45, 35, 270, "700", True),
            "supportYears": _position(46.2, 58.9, 34, 90),
            "issuedYear": _position(72.15, 80.95, 31, 92),
            "issuedMonth": _position(77.85, 80.95, 31, 56),
            "issuedDay": _position(81.45, 80.95, 31, 56),
        },
    },
    "directorWithoutCurrent": {
        "file": "director-without-current.jpg",
        "positions": {
            "donorName": _position(28.0, 38.75, 46, 230, "700", True),
            "totalAmountWithoutCurrent": _position(44.5, 46.45, 35, 270, "700", True),
            "supportYears": _position(46.2, 58.9, 34, 90),
            "issuedYear": _position(72.15, 80.95, 31, 92),
            "issuedMonth": _position(77.85, 80.95, 31, 56),
            "issuedDay": _position(81.45, 80.95, 31, 56),
        },
    },
}


def select_certificate_template(member_level: str, current_year_amount: Decimal) -> str:
    is_director = member_level == "director"
    has_current = current_year_amount > 0
    if is_director and has_current:
        return "directorWithCurrent"
    if is_director:
        return "directorWithoutCurrent"
    if has_current:
        return "memberWithCurrent"
    return "memberWithoutCurrent"


def generate_certificate_image(
    *,
    donor_name: str,
    total_amount: Decimal,
    current_year_amount: Decimal,
    support_years: int,
    issued_on: date,
    member_level: str,
) -> tuple[str, str]:
    template_key = select_certificate_template(member_level, current_year_amount)
    template = TEMPLATE_CONFIG[template_key]

    upload_dir = Path(settings.UPLOAD_DIR)
    template_path = upload_dir / "certificate-templates" / template["file"]
    if not template_path.exists():
        raise FileNotFoundError(f"Certificate template not found: {template_path}")

    output_dir = upload_dir / "member-certificates"
    output_dir.mkdir(parents=True, exist_ok=True)

    image = Image.open(template_path).convert("RGB")
    draw = ImageDraw.Draw(image)
    positions = template["positions"]

    _draw_field(draw, positions, "donorName", donor_name, "name")
    if current_year_amount > 0:
        _draw_field(draw, positions, "currentAmount", _format_amount(current_year_amount), "number")
        _draw_field(draw, positions, "totalAmountWithCurrent", _format_amount(total_amount), "number")
    else:
        _draw_field(draw, positions, "totalAmountWithoutCurrent", _format_amount(total_amount), "number")

    _draw_field(draw, positions, "supportYears", str(support_years or 1), "number")
    _draw_field(draw, positions, "issuedYear", str(issued_on.year), "number")
    _draw_field(draw, positions, "issuedMonth", str(issued_on.month), "number")
    _draw_field(draw, positions, "issuedDay", str(issued_on.day), "number")

    filename = f"certificate-{template_key}-{uuid.uuid4().hex}.jpg"
    output_path = output_dir / filename
    image.save(output_path, "JPEG", quality=95, optimize=True)

    origin = (settings.PUBLIC_ASSET_ORIGIN or "").strip().rstrip("/")
    return template_key, f"{origin}/uploads/member-certificates/{filename}" if origin else f"/uploads/member-certificates/{filename}"


def _draw_field(draw: ImageDraw.ImageDraw, positions: dict, key: str, text: str, font_kind: str) -> None:
    item = positions.get(key)
    if not item:
        return

    x = CANVAS_WIDTH * item["left"] / 100
    y = CANVAS_HEIGHT * item["top"] / 100
    font = _load_font(font_kind, item["size"])
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    fill = (28, 24, 20) if item.get("emphasis") else (48, 42, 36)
    text_x = x - width / 2
    text_y = y - height / 2
    draw.text((text_x, text_y), text, font=font, fill=fill)
    if item.get("emphasis"):
        draw.text((text_x + 0.8, text_y), text, font=font, fill=fill)


def _format_amount(value: Decimal) -> str:
    return f"{Decimal(str(value or 0)).quantize(Decimal('1')):,}"


def _load_font(kind: str, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in _font_candidates(kind):
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def _font_candidates(kind: str) -> list[Path]:
    upload_fonts = Path(settings.UPLOAD_DIR) / "fonts"
    app_fonts = Path(__file__).resolve().parents[2] / "assets" / "fonts"
    if kind == "number":
        names = [
            os.getenv("CERTIFICATE_NUMBER_FONT_PATH", ""),
            str(upload_fonts / "times.ttf"),
            str(upload_fonts / "Times_New_Roman.ttf"),
            str(app_fonts / "times.ttf"),
            str(app_fonts / "Times_New_Roman.ttf"),
            "C:/Windows/Fonts/times.ttf",
            "C:/Windows/Fonts/timesbd.ttf",
            "/usr/share/fonts/truetype/msttcorefonts/Times_New_Roman.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        ]
    else:
        names = [
            os.getenv("CERTIFICATE_NAME_FONT_PATH", ""),
            str(upload_fonts / "kaiti.ttf"),
            str(upload_fonts / "simkai.ttf"),
            str(upload_fonts / "NotoSerifCJK-Regular.ttc"),
            str(upload_fonts / "NotoSansCJK-Regular.ttc"),
            str(app_fonts / "kaiti.ttf"),
            str(app_fonts / "simkai.ttf"),
            str(app_fonts / "NotoSerifCJK-Regular.ttc"),
            str(app_fonts / "NotoSansCJK-Regular.ttc"),
            "C:/Windows/Fonts/simkai.ttf",
            "C:/Windows/Fonts/STKAITI.TTF",
            "C:/Windows/Fonts/STFANGSO.TTF",
            "C:/Windows/Fonts/simsun.ttc",
            "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc",
            "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
            "/usr/share/fonts/opentype/noto/NotoSerifCJKsc-Regular.otf",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/noto/NotoSerifCJK-Regular.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/arphic/ukai.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        ]
    return [Path(name) for name in names if name]
