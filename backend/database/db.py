from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

# ─── Database URL ─────────────────────────────────────────────
DATABASE_URL = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

# ─── Engine & Session ─────────────────────────────────────────
engine = create_engine(DATABASE_URL, echo=False)  # echo=True logs all SQL queries
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ─── Base class for all models ────────────────────────────────
Base = declarative_base()


# ─── Dependency — use this to get a DB session anywhere ───────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()