from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from air_quality_intelligence.service import AirQualityService


BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"


app = FastAPI(
    title="Air Quality Intelligence",
    description="Intelligent air-quality analysis dashboard",
    version="1.0.0",
)


app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static",
)


service = AirQualityService()


@app.get("/", response_class=HTMLResponse)
def home():
    index_file = TEMPLATES_DIR / "index.html"

    return index_file.read_text(
        encoding="utf-8"
    )


@app.get("/api/air-quality/{city}")
def get_air_quality(city: str):
    result = service.get_city_analysis(city)

    if result.get("status") == "No data":
        raise HTTPException(
            status_code=404,
            detail=result.get(
                "message",
                "Air quality data is not available.",
            ),
        )

    return result


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Air Quality Intelligence",
    }