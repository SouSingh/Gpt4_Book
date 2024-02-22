from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.utils.load_env import getenv

DB_URL = getenv("DB_URL")

engine = create_engine(DB_URL, pool_size=10, max_overflow=20, pool_timeout=15)
conn = engine.connect()
Session = sessionmaker(bind=engine)
Base = declarative_base()
