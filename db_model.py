from sqlalchemy import Column, String, Integer, DateTime
from datetime import datetime

from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ContactModel(Base):
    __tablename__ = "contact"
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, index=True)
    phone = Column(String, index=True)
    linkedId = Column(Integer, nullable=True)
    linkPrecedence = Column(String)
    createdAt = Column(DateTime, default=datetime.now())
    updatedAt = Column(DateTime, default=datetime.now())
    deletedAt = Column(DateTime, default=None)
