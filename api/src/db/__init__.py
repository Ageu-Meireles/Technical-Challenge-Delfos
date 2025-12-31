from sqlalchemy import create_engine
from sqlmodel import Session

from src.core import settings

engine = create_engine(settings.source_db_url)


def get_session() -> Session:
    with Session(engine) as session:
        try:
            yield session
        except Exception as exc:
            session.rollback()
            raise exc
        finally:
            session.close()
