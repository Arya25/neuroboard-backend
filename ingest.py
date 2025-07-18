import asyncio
from datetime import datetime
from faker import Faker
import random
from db import async_session
from models import Participant

fake = Faker()

diagnoses = ["ADHD", "Autism", "Dyslexia", "Anxiety", "Depression"]
states = ["NY", "CA", "TX", "FL", "IL"]
genders = ["Male", "Female", "Other"]

async def insert_fake_participant():
    external_id = f"A{random.randint(10000, 99999)}"
    new_participant = Participant(
        external_id=external_id,
        diagnosis=random.choice(diagnoses),
        age=random.randint(3, 18),
        gender=random.choice(genders),
        state=random.choice(states),
        joined_at=datetime.utcnow()
    )

    async with async_session() as session:
        session.add(new_participant)
        await session.commit()
        print(f"Inserted: {external_id} | Age: {new_participant.age} | {new_participant.state}")

async def run_ingestor():
    while True:
        await insert_fake_participant()
        await asyncio.sleep(30)  # Wait 30 seconds before adding next
