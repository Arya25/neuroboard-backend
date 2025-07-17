import json
from datetime import datetime
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from db import async_session, engine
from models import Participant, Base
from sqlalchemy import text

async def seed_bulk():
    print("📥 Loading data from bulk_data.json...")
    with open("bulk_data.json") as f:
        data = json.load(f)

    participants = []
    for item in data:
        participant = Participant(
            external_id=item["external_id"],
            diagnosis=item["diagnosis"],
            age=item["age"],
            gender=item["gender"],
            state=item["state"],
            joined_at=datetime.fromisoformat(item["joined_at"])
        )
        participants.append(participant)

    print(f"🚀 Inserting {len(participants)} records into PostgreSQL...")

    async with async_session() as session:
        async with session.begin():
            await session.execute(text("DELETE FROM participants"))  # clear old data (optional)
            session.add_all(participants)

        await session.commit()

    print("✅ Seeding complete!")

# Create tables and run seed function
async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_bulk()

if __name__ == "__main__":
    asyncio.run(main())
