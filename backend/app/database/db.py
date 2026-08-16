import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import tempfile

if os.getenv("VERCEL"):
    db_path = os.path.join(tempfile.gettempdir(), "svamitva_drone.db")
    default_db = f"sqlite:///{db_path}"
else:
    default_db = "sqlite:///./svamitva_drone.db"

DATABASE_URL = os.getenv("DATABASE_URL", default_db)

# For SQLite, enable check_same_thread=False
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
