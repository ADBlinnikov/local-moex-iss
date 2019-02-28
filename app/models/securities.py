from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from .base import Base


class Securities(Base):

    __tablename__ = "securities"

    uid = Column(Integer, primary_key=True)
    secid = Column(String(36))
    data = Column(JSONB, nullable=True)

