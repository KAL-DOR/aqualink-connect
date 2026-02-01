from fastapi import APIRouter, Depends
from typing import List
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.sql import func

from app.database import get_db, Base

router = APIRouter()


# Model
class Hotspot(Base):
    __tablename__ = "hotspots"

    id = Column(Integer, primary_key=True, index=True)
    cluster_label = Column(Integer)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    risk_index = Column(Float)
    location_name = Column(String(100))
    sampled_reports = Column(Integer)
    estimated_total_reports = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())


# Response models
class HotspotResponse(BaseModel):
    id: int
    cluster_label: int
    lat: float
    lon: float
    risk_index: float
    location_name: str
    sampled_reports: int
    estimated_total_reports: int

    class Config:
        from_attributes = True


class HotspotsListResponse(BaseModel):
    hotspots: List[HotspotResponse]
    total: int
    max_risk: float
    min_risk: float


@router.get("", response_model=HotspotsListResponse)
async def get_hotspots(db: Session = Depends(get_db)):
    """
    Get all hotspots/risk zones for map display.
    """
    hotspots = db.query(Hotspot).order_by(Hotspot.risk_index.desc()).all()

    risk_values = [h.risk_index for h in hotspots if h.risk_index]

    return HotspotsListResponse(
        hotspots=[
            HotspotResponse(
                id=h.id,
                cluster_label=h.cluster_label or 0,
                lat=h.lat,
                lon=h.lon,
                risk_index=h.risk_index or 0,
                location_name=h.location_name or "",
                sampled_reports=h.sampled_reports or 0,
                estimated_total_reports=h.estimated_total_reports or 0
            )
            for h in hotspots
        ],
        total=len(hotspots),
        max_risk=max(risk_values) if risk_values else 0,
        min_risk=min(risk_values) if risk_values else 0
    )


@router.get("/summary")
async def get_hotspots_summary(db: Session = Depends(get_db)):
    """
    Get summary statistics for hotspots.
    """
    hotspots = db.query(Hotspot).all()

    by_location = {}
    for h in hotspots:
        name = h.location_name or "Unknown"
        if name not in by_location:
            by_location[name] = {"count": 0, "total_reports": 0, "avg_risk": 0, "risks": []}
        by_location[name]["count"] += 1
        by_location[name]["total_reports"] += h.estimated_total_reports or 0
        by_location[name]["risks"].append(h.risk_index or 0)

    for name in by_location:
        risks = by_location[name]["risks"]
        by_location[name]["avg_risk"] = sum(risks) / len(risks) if risks else 0
        del by_location[name]["risks"]

    return {
        "total_hotspots": len(hotspots),
        "by_location": by_location,
        "total_estimated_reports": sum(h.estimated_total_reports or 0 for h in hotspots)
    }
