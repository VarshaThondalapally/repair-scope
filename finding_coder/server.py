"""Local web page and JSON API (FastAPI). Stateless: an uploaded catalog travels with each request."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import api
from .catalog import CatalogError
from .domains import DomainPack, list_domains, load_domain, pack_from_catalog_text
from .export import ExportError

WEB = Path(__file__).resolve().parent.parent / "web"
PAGE = WEB / "index.html"

app = FastAPI(title="repair-scope", docs_url=None, redoc_url=None, openapi_url=None)


class Query(BaseModel):
    """What the page sends: a bundled domain name OR the text of an uploaded catalog CSV."""

    domain: str | None = None
    catalog_csv: str | None = Field(default=None, max_length=1_000_000)
    finding: str = Field(default="", max_length=2000)
    codes: list[str] = Field(default_factory=list, max_length=100)
    allow_incomplete: bool = False
    review_confirmed: bool = False
    reviewer: str = Field(default="", max_length=100)
    override_reason: str = Field(default="", max_length=1000)


@lru_cache(maxsize=None)
def _bundled(name: str) -> DomainPack:
    return load_domain(name)


def _pack(query: Query) -> DomainPack:
    if query.catalog_csv is not None:
        try:
            return pack_from_catalog_text(query.catalog_csv)
        except CatalogError as error:
            raise HTTPException(status_code=400, detail=error.problems)
    if query.domain in list_domains():
        return _bundled(query.domain)
    raise HTTPException(status_code=400, detail=[f"Unknown domain {query.domain!r}."])


@app.get("/", response_class=HTMLResponse)
def page() -> str:
    return PAGE.read_text(encoding="utf-8")


@app.get("/api/domains")
def domains() -> list[dict]:
    return [api.describe(_bundled(name)) for name in list_domains()]


@app.post("/api/catalog")
def catalog(query: Query) -> dict:
    """Validate a catalog (bundled or uploaded) and describe it."""
    return api.describe(_pack(query))


@app.post("/api/match")
def match(query: Query) -> dict:
    return api.run_match(_pack(query), query.finding)


@app.post("/api/check")
def check(query: Query) -> dict:
    return api.run_check(_pack(query), query.finding, query.codes)


@app.post("/api/export", response_class=PlainTextResponse)
def export(query: Query) -> PlainTextResponse:
    if not query.review_confirmed or not query.reviewer.strip():
        raise HTTPException(status_code=409, detail=["Explicit review confirmation and reviewer name are required."])
    if query.allow_incomplete and len(query.override_reason.strip()) < 10:
        raise HTTPException(status_code=409, detail=["Explain the incomplete-set override in at least 10 characters."])
    if not query.finding.strip() or not query.codes:
        raise HTTPException(status_code=400, detail=["A finding and selected codes are required."])
    try:
        text = api.run_export(_pack(query), query.finding, query.codes, query.allow_incomplete)
    except ExportError as error:
        raise HTTPException(status_code=409, detail=[str(error)])
    return PlainTextResponse(
        text,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="approved_lines.csv"'},
    )


@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
    return response


app.mount("/", StaticFiles(directory=WEB), name="web")
