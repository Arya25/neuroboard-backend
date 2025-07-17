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
from sqlalchemy import and_, select


app = FastAPI(title="NeuroBoard")

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


