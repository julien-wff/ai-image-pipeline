from sqlalchemy import (
    create_engine,
    Integer,
    String,
    DateTime,
    Float,
    Text,
    Enum as SQLEnum,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, mapped_column, Mapped
from datetime import datetime
import enum

from app.config import settings

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ProcessingStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ImageLabel(str, enum.Enum):
    PAINTING = "painting"
    PHOTO = "photo"
    SCHEMATIC = "schematic"
    SKETCH = "sketch"
    TEXT = "text"


class ImageRecord(Base):
    __tablename__ = "images"

    # Technical fields
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    status: Mapped[ProcessingStatus] = mapped_column(
        SQLEnum(ProcessingStatus), default=ProcessingStatus.PENDING
    )

    # File
    original_filename: Mapped[str] = mapped_column(String, nullable=False)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    upload_path: Mapped[str] = mapped_column(String, nullable=False)
    processed_path: Mapped[str] = mapped_column(String, nullable=True)

    # Processing details
    processed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    processing_time: Mapped[float] = mapped_column(Float, nullable=True)  # in seconds
    error_message: Mapped[str] = mapped_column(Text, nullable=True)

    # Image attributes
    label: Mapped[ImageLabel] = mapped_column(SQLEnum(ImageLabel), nullable=True)
    caption: Mapped[str] = mapped_column(Text, nullable=True)


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
