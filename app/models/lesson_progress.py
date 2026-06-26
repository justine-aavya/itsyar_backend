# import uuid
# from datetime import datetime
# from sqlalchemy import String, DateTime, Float, Boolean
# from sqlalchemy.orm import Mapped, mapped_column
# from app.db.base import Base


# class LessonProgress(Base):
#     __tablename__ = "lesson_progress"

#     id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
#     user_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
#     course_id: Mapped[str] = mapped_column(String, nullable=False)
#     module_id: Mapped[str] = mapped_column(String, nullable=False)
#     played_seconds: Mapped[float] = mapped_column(Float, default=0.0)
#     total_seconds: Mapped[float] = mapped_column(Float, default=0.0)
#     is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
#     updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
