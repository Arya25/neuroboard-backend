from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True)
    diagnosis = Column(String)
    age = Column(Integer)
    gender = Column(String)
    state = Column(String)
    joined_at = Column(DateTime)
