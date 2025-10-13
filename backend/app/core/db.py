from sqlmodel import create_engine

from app.core.config import settings

# Create the database engine
engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
