from sqlalchemy import Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import TIMESTAMP

# Shared declarative base for all models
Base = declarative_base()


class TimestampMixin:
    """Mixin providing automatic timestamp fields for models."""

    created_at = Column(
        TIMESTAMP(timezone=True),
        default=func.now(),
        nullable=False,
        index=True
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False
    )