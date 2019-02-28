from sqlalchemy import Column, String, Date, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from .base import Base


class History(Base):

    __tablename__ = "history"
    __table_args__ = (PrimaryKeyConstraint("secid", "tradedate"), {})

    secid = Column(String(36), index=True)
    tradedate = Column(Date, index=True)
    group = Column(String(120), index=True)
    assetcode = Column(String(10), nullable=True)
    expiration = Column(Date, nullable=True)
    data = Column(JSONB, nullable=True)

    security = relationship(
        "Securities",
        primaryjoin="foreign(History.secid) == remote(Securities.secid)",
        uselist=False,
        viewonly=True,
    )

