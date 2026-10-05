from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from typing import Generator
import os

from app.config import get_settings

settings = get_settings()

db_url = os.getenv("DATABASE_URL", settings.DATABASE_URL)

connect_args = {}
if db_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False
    engine = create_engine(db_url, connect_args=connect_args)
else:
    engine = create_engine(
        db_url,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
