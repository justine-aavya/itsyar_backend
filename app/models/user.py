
############################################################################################################


# import uuid

# from datetime import datetime

# from sqlalchemy import String, DateTime, Integer

# from sqlalchemy.orm import Mapped, mapped_column

# from app.db.base import Base





# class User(Base):

#     __tablename__ = "users"



#     id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

#     email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)

#     hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

#     full_name: Mapped[str] = mapped_column(String(255), nullable=False)

#     role: Mapped[str] = mapped_column(String(50), nullable=False)  # "Student" or "Participant"

#     learning_interest: Mapped[str] = mapped_column(String(100), nullable=True)  # Only for Students

#     created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)



#     # Track security state. Incrementing this instantly revokes all active refresh tokens.

#     token_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False) 

###############################################################################################################################

import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=True)  # ← Changed: nullable for Google users
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    learning_interest: Mapped[str] = mapped_column(String(100), nullable=True)
    auth_provider: Mapped[str] = mapped_column(String(20), default="local", nullable=False)  # ← NEW: "local", "google", "both"
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    token_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
