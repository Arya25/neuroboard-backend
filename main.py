from fastapi import FastAPI, Query
import asyncio
from db import init_db
import json
from datetime import datetime
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db import get_session
from models import Participant
from ingest import run_ingestor

from typing import Optional, List
from sqlalchemy import and_, select, func
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI(title="NeuroBoard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:5173"] to be stricter
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await init_db()
    asyncio.create_task(run_ingestor())
    print("Database initialized.")

@app.post("/seed")
async def seed_data(session: AsyncSession = Depends(get_session)):
    with open("seed_data.json") as f:
        participants = json.load(f)

    for item in participants:
        participant = Participant(
            external_id=item["external_id"],
            diagnosis=item["diagnosis"],
            age=item["age"],
            gender=item["gender"],
            state=item["state"],
            joined_at=datetime.fromisoformat(item["joined_at"])
        )
        session.add(participant)

    await session.commit()
    return {"message": f"{len(participants)} participants added"}

@app.get("/participants")
async def get_participants(
    state: Optional[str] = None,
    gender: Optional[str] = None,
    diagnosis: Optional[str] = None,
    age_min: Optional[int] = None,
    age_max: Optional[int] = None,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session)
):
    filters = []

    if state:
        filters.append(Participant.state == state)
    if gender:
        filters.append(Participant.gender == gender)
    if diagnosis:
        filters.append(Participant.diagnosis == diagnosis)
    if age_min is not None:
        filters.append(Participant.age >= age_min)
    if age_max is not None:
        filters.append(Participant.age <= age_max)

    stmt = select(Participant).where(and_(*filters)).offset(offset).limit(limit)
    result = await session.execute(stmt)
    participants = result.scalars().all()
    return [p.__dict__ for p in participants]

@app.get("/participants/count")
async def get_participant_count(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(func.count()).select_from(Participant))
    count = result.scalar()
    return {"count": count}

@app.get("/chart-data/gender")
async def get_gender_chart_data(
    state: Optional[str] = None,
    diagnosis: Optional[str] = None,
    age_min: Optional[int] = None,
    age_max: Optional[int] = None,
    session: AsyncSession = Depends(get_session)
):
    filters = []

    if state:
        filters.append(Participant.state == state)
    if diagnosis:
        filters.append(Participant.diagnosis == diagnosis)
    if age_min is not None:
        filters.append(Participant.age >= age_min)
    if age_max is not None:
        filters.append(Participant.age <= age_max)

    stmt = (
        select(Participant.gender, func.count(Participant.id))
        .where(and_(*filters))
        .group_by(Participant.gender)
    )

    result = await session.execute(stmt)
    data = result.all()

    return [{"label": gender, "value": count} for gender, count in data]

@app.get("/chart-data/state")
async def get_state_chart_data(
    gender: Optional[str] = None,
    diagnosis: Optional[str] = None,
    age_min: Optional[int] = None,
    age_max: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
):
    filters = build_filters(None, gender, diagnosis, age_min, age_max)
    stmt = select(Participant.state, func.count(Participant.id)).where(
        and_(*filters)
    ).group_by(Participant.state)
    result = await session.execute(stmt)
    data = result.all()
    return [{"label": state, "value": count} for state, count in data]

@app.get("/chart-data/age")
async def get_age_chart_data(
    gender: Optional[str] = None,
    state: Optional[str] = None,
    diagnosis: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
):
    filters = build_filters(state, gender, diagnosis, None, None)
    stmt = select(Participant.age, func.count(Participant.id)).where(
        and_(*filters)
    ).group_by(Participant.age).order_by(Participant.age)
    result = await session.execute(stmt)
    data = result.all()
    return [{"label": str(age), "value": count} for age, count in data]

@app.get("/chart-data/diagnosis")
async def get_diagnosis_chart_data(
    gender: Optional[str] = None,
    state: Optional[str] = None,
    age_min: Optional[int] = None,
    age_max: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
):
    filters = build_filters(state, gender, None, age_min, age_max)
    stmt = select(Participant.diagnosis, func.count(Participant.id)).where(
        and_(*filters)
    ).group_by(Participant.diagnosis)
    result = await session.execute(stmt)
    data = result.all()
    return [{"label": diagnosis, "value": count} for diagnosis, count in data]


def build_filters(
    state: Optional[str],
    gender: Optional[str],
    diagnosis: Optional[str],
    age_min: Optional[int],
    age_max: Optional[int]
):
    filters = []
    if state:
        filters.append(Participant.state == state)
    if gender:
        filters.append(Participant.gender == gender)
    if diagnosis:
        filters.append(Participant.diagnosis == diagnosis)
    if age_min is not None:
        filters.append(Participant.age >= age_min)
    if age_max is not None:
        filters.append(Participant.age <= age_max)
    return filters

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
