from sqlalchemy import Column, Integer, String
from .database import Base

class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    short_code = Column(String, unique=True, index=True, nullable=False)
    long_url = Column(String, index=True, nullable=False)
    hits = Column(Integer, default=0)