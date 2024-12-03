from sqlalchemy import Column, Integer, String
from models.base import Base

class ClassEnumDB(Base):
    __tablename__ = 'class_ref'
    id = Column(Integer, primary_key=True, autoincrement=True)
    display_name = Column(String, nullable=False, unique=True)

class RacesEnumDB(Base):
    __tablename__ = 'races_ref'
    id = Column(Integer, primary_key=True, autoincrement=True)
    display_name = Column(String, nullable=False, unique=True)

class StatsEnumDB(Base):
    __tablename__ = 'stats_ref'
    id = Column(Integer, primary_key=True, autoincrement=True)
    display_name = Column(String, nullable=False, unique=True)
    abbr = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False)
