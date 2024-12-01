from sqlalchemy import Column, Table, Integer, ForeignKey, String, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

character_inventory = Table(
    "character_inventory",
    Base.metadata,
    Column("character_id", Integer, ForeignKey("characters.id"), primary_key=True),
    Column("item_name", String, primary_key=True),
    Column("quantity", Integer, nullable=False, default=1),
)

class Inventory(Base):
    """
    SQLAlchemy ORM representation for Inventory.
    """
    __tablename__ = "inventories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    items = Column(JSON, default={})  # Store as JSON for flexibility