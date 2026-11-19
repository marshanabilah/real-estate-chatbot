from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.catalog import filter_records, load_records
from app.chat import answer_question


app = FastAPI(title="Property Discovery", version="0.1.0")
RECORDS = load_records()
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = "default-src 'self'; style-src 'self'; script-src 'self'; base-uri 'self'; frame-ancestors 'none'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response


class ChatRequest(BaseModel):
    question: str = Field(min_length=2, max_length=600)


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/properties")
def list_properties(
    source: Optional[str] = None,
    city: Optional[str] = None,
    district: Optional[str] = None,
    property_type: Optional[str] = Query(None, alias="propertyType"),
    min_bedrooms: Optional[int] = Query(None, alias="minBedrooms", ge=0),
    max_price: Optional[int] = Query(None, alias="maxPrice", ge=0),
) -> dict[str, object]:
    items = filter_records(
        RECORDS,
        source=source,
        city=city,
        district=district,
        property_type=property_type,
        min_bedrooms=min_bedrooms,
        max_price=max_price,
    )
    return {"items": items, "total": len(items)}


@app.post("/api/chat")
def chat(request: ChatRequest) -> dict[str, object]:
    if not request.question.strip():
        raise HTTPException(status_code=422, detail="Question cannot be blank")
    return answer_question(request.question, RECORDS)
