from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "sqlite:///./gxp_gov.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
    # Add new columns to existing ai_systems table (safe if columns already exist)
    with engine.connect() as conn:
        inspector = inspect(engine)
        existing_columns = {col["name"] for col in inspector.get_columns("ai_systems")}
        if "previous_version" not in existing_columns:
            conn.execute(text("ALTER TABLE ai_systems ADD COLUMN previous_version VARCHAR(50)"))
            conn.commit()
        if "obligations_synced_at" not in existing_columns:
            conn.execute(text("ALTER TABLE ai_systems ADD COLUMN obligations_synced_at DATETIME"))
            conn.commit()