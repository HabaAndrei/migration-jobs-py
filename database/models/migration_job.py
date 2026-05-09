import uuid

from sqlalchemy import Column, Integer, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP

from .utils import TimestampMixin, Base


class MigrationJob(Base, TimestampMixin):
    __tablename__ = "migration_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    description = Column(Text, nullable=False)
    executed_at = Column(TIMESTAMP(timezone=True), nullable=True)
    done = Column(Boolean, nullable=False, default=False)
    execution_time_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
