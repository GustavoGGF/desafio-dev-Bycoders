from os import getenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLACLCHEMY_DATABASE_URL = getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/cnab_db"
)

engine = create_engine(SQLACLCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()