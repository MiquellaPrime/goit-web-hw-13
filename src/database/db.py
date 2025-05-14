from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.settings import settings

engine = create_engine(url=settings.postgres.dsn)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
