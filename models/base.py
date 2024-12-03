from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeMeta

# Create the Base class for all ORM models
Base: DeclarativeMeta = declarative_base()
