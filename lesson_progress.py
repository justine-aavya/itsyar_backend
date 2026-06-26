# run_migration_progress.py
from app.db.session import engine
from app.db.base import Base
# from app.models.lesson_progress import LessonProgress

Base.metadata.create_all(bind=engine)
print("✅ lesson_progress table created")
