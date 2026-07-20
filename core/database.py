import os

from dotenv import load_dotenv
from sqlalchemy import MetaData, MetaData, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()


DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_SCHEMA = os.getenv("DB_SCHEMA", "public")


DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{DB_USER}:{DB_PASSWORD}@"
    f"{DB_HOST}:{DB_PORT}/"
    f"{DB_NAME}"
)


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    future=True,
    echo=False,
    connect_args={
        "options": f"-csearch_path={DB_SCHEMA}"
    }
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True
)


metadata = MetaData(schema=os.getenv("DB_SCHEMA"))

class Base(DeclarativeBase):
    metadata = metadata


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_engine():
    return engine