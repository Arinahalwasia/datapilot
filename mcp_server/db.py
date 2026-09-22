import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

load_dotenv()


def get_database_url() -> str:
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    database = os.getenv("POSTGRES_DB", "datapilot")
    username = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")

    return (
        f"postgresql+psycopg2://"
        f"{username}:{password}@{host}:{port}/{database}"
    )


engine: Engine = create_engine(
    get_database_url(),
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)