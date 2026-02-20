import enum
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, Integer, String, Text


from app.database import Base


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    AWAITING_CONFIRMATION = "awaiting_confirmation"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AnalysisTask(Base):
    __tablename__ = "analysis_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Manus-Pflichtfelder
    unternehmen = Column(String(500), nullable=False)
    standort = Column(String(300), nullable=False)
    position = Column(String(300), nullable=False)

    # Optionaler Zusatzkontext (aus Rich Input)
    zusatzkontext = Column(Text, nullable=True)

    # Generierter Manus-Prompt
    manus_prompt = Column(Text, nullable=True)

    # Manus-Tracking
    manus_task_id = Column(String(200), nullable=True, index=True)
    status = Column(
        Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False
    )
    result_file_url = Column(String(1000), nullable=True)
    result_file_name = Column(String(500), nullable=True)
    error_message = Column(Text, nullable=True)

    # Teams-Kontext
    teams_user_id = Column(String(200), nullable=True)
    teams_user_name = Column(String(300), nullable=True)
    teams_conversation_id = Column(String(500), nullable=True)
    teams_activity_id = Column(String(500), nullable=True)
    conversation_reference = Column(Text, nullable=True)

    # Input-Modus
    input_modus = Column(String(20), nullable=True)

    # Zeitstempel
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    completed_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return (
            f"<AnalysisTask(id={self.id}, "
            f"unternehmen='{self.unternehmen}', "
            f"status={self.status})>"
        )
