# import uuid
# from datetime import datetime

# from sqlalchemy import String, DateTime
# from sqlalchemy.orm import Mapped, mapped_column

# from app.database import Base


# class User(Base):
#     __tablename__ = "users"

#     id: Mapped[str] = mapped_column(
#         String, primary_key=True, default=lambda: str(uuid.uuid4())
#     )
#     email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
#     hashed_password: Mapped[str] = mapped_column(String(255), nullable=True)
#     full_name: Mapped[str] = mapped_column(String(255), nullable=True)
#     role: Mapped[str] = mapped_column(String(50), default="Student", nullable=False)
#     google_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=True)
#     created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
#     updated_at: Mapped[datetime] = mapped_column(
#         DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
#     )
###########################################################################################################
# # user.py
# import uuid
# from datetime import datetime
# from typing import Optional

# class User:
#     """
#     Structural interface representing a user profile within the Palantir Ontology.
#     Stripped of all legacy PostgreSQL / SQLAlchemy relational data layers.
#     """
#     def __init__(
#         self,
#         email: str,
#         hashed_password: str,
#         full_name: str,
#         role: str,
#         learning_interest: Optional[str] = None,
#         id: Optional[str] = None,
#         created_at: Optional[datetime] = None,
#         token_version: int = 1
#     ):
#         self.id = id or str(uuid.uuid4())
#         self.email = email.strip().lower()
#         self.hashed_password = hashed_password
#         self.full_name = full_name
#         self.role = role  # e.g., "Student", "Participant", "Mentor", "Admin"
#         self.learning_interest = learning_interest
#         self.created_at = created_at or datetime.utcnow()
#         self.token_version = token_version

#     @classmethod
#     def from_osdk(cls, osdk_obj: any) -> "User":
#         """
#         Factory method to parse a native Palantir OSDK Object profile 
#         into a standard Python object context wrapper.
#         """
#         if not osdk_obj:
#             raise ValueError("Cannot map an empty object node profile.")
            
#         # Handle dynamic property extraction based on upstream Ontology naming layouts
#         pk_val = getattr(osdk_obj, "id", None) or getattr(osdk_obj, "primary_key", None) or getattr(osdk_obj, "userId", None)
        
#         return cls(
#             id=str(pk_val) if pk_val else str(uuid.uuid4()),
#             email=getattr(osdk_obj, "email", ""),
#             hashed_password=getattr(osdk_obj, "hashed_password", getattr(osdk_obj, "password", "")),
#             full_name=getattr(osdk_obj, "full_name", getattr(osdk_obj, "name", "")),
#             role=getattr(osdk_obj, "role", "Student"),
#             learning_interest=getattr(osdk_obj, "learning_interest", None),
#             token_version=int(getattr(osdk_obj, "token_version", 1))
#         )

#     def to_dict(self) -> dict:
#         """Serializes properties cleanly into an standard exchange payload."""
#         return {
#             "id": self.id,
#             "email": self.email,
#             "full_name": self.full_name,
#             "role": self.role,
#             "learning_interest": self.learning_interest,
#             "token_version": self.token_version,
#             "created_at": self.created_at.isoformat() if self.created_at else None
#         }
############################################################################################################


import uuid

from datetime import datetime

from sqlalchemy import String, DateTime, Integer

from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base





class User(Base):

    __tablename__ = "users"



    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)

    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    full_name: Mapped[str] = mapped_column(String(255), nullable=False)

    role: Mapped[str] = mapped_column(String(50), nullable=False)  # "Student" or "Participant"

    learning_interest: Mapped[str] = mapped_column(String(100), nullable=True)  # Only for Students

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)



    # Track security state. Incrementing this instantly revokes all active refresh tokens.

    token_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False) 

