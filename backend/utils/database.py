from sqlalchemy import create_engine, TIMESTAMP, Column, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles
from backend.config import settings


engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ISTNow(expression.FunctionElement):
    """Used to calculate IST now timestamp"""
    type = DateTime()


@compiles(ISTNow, "postgresql")
def pg_istnow(element, compiler, **kw):
    """Compiles istnow for postgres"""
    return "TIMEZONE('Asia/Kolkata', CURRENT_TIMESTAMP)"


class BaseMixin:
    """Mixin for database tables"""
    added_on = Column(TIMESTAMP, server_default=ISTNow())
    updated_on = Column(TIMESTAMP, onupdate=ISTNow())