# auth/models.py
from sqlalchemy import Column, Integer, String
from config.db import Base

class User(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)

