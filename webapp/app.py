import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data.json"

app = FastAPI(title="Teacher Taplink Site")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


def _load_data() -> Dict[str, Any]:
    if not DATA_FILE.exists():
        return {}
    with DATA_FILE.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _save_data(payload: Dict[str, Any]) -> None:
    payload["updatedAt"] = datetime.utcnow().isoformat()
    with DATA_FILE.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def _find_item(items: List[Dict[str, Any]], item_id: str) -> Optional[Dict[str, Any]]:
    for item in items:
        if item.get("id") == item_id:
            return item
    return None


def _slugify(value: str) -> str:
    value = re.sub(r"[^\w\s-]", "", value, flags=re.U).strip().lower()
    value = re.sub(r"[\s_-]+", "-", value, flags=re.U)
    return value or "item"


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    data = _load_data()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "data": data},
    )


@app.get("/admin", response_class=HTMLResponse)
def admin_home(request: Request) -> HTMLResponse:
    data = _load_data()
    return templates.TemplateResponse(
        "admin/index.html",
        {"request": request, "data": data},
    )


@app.get("/admin/{section}", response_class=HTMLResponse)
def admin_section(request: Request, section: str) -> HTMLResponse:
    data = _load_data()
    template_map = {
        "meta": "admin/meta.html",
        "content": "admin/content.html",
        "services": "admin/services.html",
        "pricing": "admin/pricing.html",
        "groups": "admin/groups.html",
        "testimonials": "admin/testimonials.html",
        "parsers": "admin/parsers.html",
    }
    template_name = template_map.get(section)
    if not template_name:
        raise HTTPException(status_code=404, detail="Section not found")
    return templates.TemplateResponse(
        template_name,
        {"request": request, "data": data},
    )


@app.get("/api/data")
def api_data() -> Dict[str, Any]:
    return _load_data()


@app.post("/api/meta")
def update_meta(
    title: str = Form(...),
    description: str = Form(...),
    keywords: str = Form(""),
    og_title: str = Form(""),
    og_description: str = Form(""),
) -> Dict[str, Any]:
    data = _load_data()
    data["meta"] = {
        "title": title,
        "description": description,
        "keywords": keywords,
        "og_title": og_title,
        "og_description": og_description,
    }
    _save_data(data)
    return {"status": "ok"}


@app.post("/api/content")
def update_content(
    hero_title: str = Form(...),
    hero_subtitle: str = Form(...),
    hero_badge: str = Form(""),
    about_title: str = Form(...),
    about_text: str = Form(...),
    about_quote: str = Form(""),
    cta_title: str = Form(...),
    cta_text: str = Form(...),
) -> Dict[str, Any]:
    data = _load_data()
    data["content"] = {
        "hero_title": hero_title,
        "hero_subtitle": hero_subtitle,
        "hero_badge": hero_badge,
        "about_title": about_title,
        "about_text": about_text,
        "about_quote": about_quote,
        "cta_title": cta_title,
        "cta_text": cta_text,
    }
    _save_data(data)
    return {"status": "ok"}


@app.post("/api/services")
def save_service(
    mode: str = Form(...),
    name: str = Form(...),
    description: str = Form(...),
    duration: str = Form(...),
    price: str = Form(...),
    item_id: str = Form(""),
) -> Dict[str, Any]:
    data = _load_data()
    services = data.get("services", [])
    if mode == "delete":
        data["services"] = [item for item in services if item.get("id") != item_id]
        _save_data(data)
        return {"status": "ok"}
    if mode == "update":
        item = _find_item(services, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Service not found")
        item.update(
            {"name": name, "description": description, "duration": duration, "price": price}
        )
    else:
        services.append(
            {
                "id": f"service-{_slugify(name)}-{len(services)+1}",
                "name": name,
                "description": description,
                "duration": duration,
                "price": price,
            }
        )
        data["services"] = services
    _save_data(data)
    return {"status": "ok"}


@app.post("/api/prices")
def save_price(
    mode: str = Form(...),
    name: str = Form(...),
    description: str = Form(...),
    price: str = Form(...),
    item_id: str = Form(""),
) -> Dict[str, Any]:
    data = _load_data()
    prices = data.get("pricing", [])
    if mode == "delete":
        data["pricing"] = [item for item in prices if item.get("id") != item_id]
        _save_data(data)
        return {"status": "ok"}
    if mode == "update":
        item = _find_item(prices, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Price not found")
        item.update({"name": name, "description": description, "price": price})
    else:
        prices.append(
            {
                "id": f"price-{_slugify(name)}-{len(prices)+1}",
                "name": name,
                "description": description,
                "price": price,
            }
        )
        data["pricing"] = prices
    _save_data(data)
    return {"status": "ok"}


@app.post("/api/groups")
def save_group(
    mode: str = Form(...),
    name: str = Form(...),
    description: str = Form(...),
    schedule: str = Form(...),
    price: str = Form(...),
    format_name: str = Form(...),
    item_id: str = Form(""),
) -> Dict[str, Any]:
    data = _load_data()
    groups = data.get("groups", [])
    if mode == "delete":
        data["groups"] = [item for item in groups if item.get("id") != item_id]
        _save_data(data)
        return {"status": "ok"}
    if mode == "update":
        item = _find_item(groups, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Group not found")
        item.update(
            {
                "name": name,
                "description": description,
                "schedule": schedule,
                "price": price,
                "format": format_name,
            }
        )
    else:
        groups.append(
            {
                "id": f"group-{_slugify(name)}-{len(groups)+1}",
                "name": name,
                "description": description,
                "schedule": schedule,
                "price": price,
                "format": format_name,
            }
        )
        data["groups"] = groups
    _save_data(data)
    return {"status": "ok"}


@app.post("/api/testimonials")
def save_testimonial(
    mode: str = Form(...),
    name: str = Form(...),
    text: str = Form(...),
    tag: str = Form(...),
    item_id: str = Form(""),
) -> Dict[str, Any]:
    data = _load_data()
    testimonials = data.get("testimonials", [])
    if mode == "delete":
        data["testimonials"] = [item for item in testimonials if item.get("id") != item_id]
        _save_data(data)
        return {"status": "ok"}
    if mode == "update":
        item = _find_item(testimonials, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Testimonial not found")
        item.update({"name": name, "text": text, "tag": tag})
    else:
        testimonials.append(
            {
                "id": f"testimonial-{_slugify(name)}-{len(testimonials)+1}",
                "name": name,
                "text": text,
                "tag": tag,
            }
        )
        data["testimonials"] = testimonials
    _save_data(data)
    return {"status": "ok"}


@app.post("/api/parser/content")
def parse_content(url: str = Form(...)) -> JSONResponse:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise HTTPException(status_code=400, detail=f"Fetch error: {exc}") from exc
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    description = ""
    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc and meta_desc.get("content"):
        description = meta_desc["content"].strip()
    h1 = ""
    h1_tag = soup.find("h1")
    if h1_tag:
        h1 = h1_tag.get_text(strip=True)
    paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
    summary = next((p for p in paragraphs if len(p) > 60), "")
    keywords = []
    meta_keywords = soup.find("meta", attrs={"name": "keywords"})
    if meta_keywords and meta_keywords.get("content"):
        keywords = [k.strip() for k in meta_keywords["content"].split(",") if k.strip()]
    return JSONResponse(
        {
            "title": title,
            "description": description,
            "h1": h1,
            "summary": summary,
            "keywords": keywords[:12],
        }
    )


@app.post("/api/parser/reviews")
def parse_reviews(url: str = Form(...)) -> JSONResponse:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise HTTPException(status_code=400, detail=f"Fetch error: {exc}") from exc
    soup = BeautifulSoup(response.text, "html.parser")
    candidates = []
    for tag in soup.find_all(["blockquote", "div", "article"]):
        class_name = " ".join(tag.get("class", []))
        if re.search(r"review|testimonial|comment|feedback", class_name, re.I):
            text = tag.get_text(" ", strip=True)
            if 40 <= len(text) <= 320:
                candidates.append(text)
    if not candidates:
        paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
        candidates = [p for p in paragraphs if 40 <= len(p) <= 220][:6]
    data = [
        {"name": f"Отзыв {idx + 1}", "text": text, "tag": "Импортировано"}
        for idx, text in enumerate(candidates[:6])
    ]
    return JSONResponse({"items": data})

