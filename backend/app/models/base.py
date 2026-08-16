from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """
    SQLAlchemy 2.0 declarative base. 
    All future ORM models will inherit from this.
    """
    pass