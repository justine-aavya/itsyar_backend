from datetime import datetime, timedelta
from typing import Optional, List
import uuid

from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError

import bcrypt
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User

security_scheme = HTTPBearer()

# ─────────────────────────────────────────────

# Password Utilities

# ─────────────────────────────────────────────
def hash_password(password: str) -> str:  
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:

    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )
# ─────────────────────────────────────────────
# Token Generation Utilities
# ─────────────────────────────────────────────
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()

    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))

    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)





def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:

    to_encode = data.copy()

    expire = datetime.utcnow() + (expires_delta or timedelta(days=settings.REMEMBER_ME_EXPIRE_DAYS))

    to_encode.update({"exp": expire, "type": "refresh"})

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)





def create_password_reset_token(user_id: str, current_hashed_password: str) -> str:

    expire = datetime.utcnow() + timedelta(minutes=15)

    unique_secret = f"{settings.SECRET_KEY}{current_hashed_password}"

    to_encode = {"sub": user_id, "exp": expire, "purpose": "password_reset"}

    return jwt.encode(to_encode, unique_secret, algorithm=settings.ALGORITHM)



# ─────────────────────────────────────────────

# Authentication Dependencies (Manual Header Extraction)

# ─────────────────────────────────────────────



# async def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:

#     """Reads and validates the JWT access token straight from the raw request headers."""

#     auth_header = request.headers.get("Authorization")

   

#     if not auth_header:

#         raise HTTPException(

#             status_code=status.HTTP_401_UNAUTHORIZED,

#             detail="Missing Authorization Header. Please provide 'Bearer <access_token>'",

#         )

       

#     try:

#         # Expecting the value pattern string format: "Bearer eyJhbGci..."

#         token_type, token = auth_header.split(" ")

#         if token_type.lower() != "bearer":

#             raise HTTPException(

#                 status_code=status.HTTP_401_UNAUTHORIZED,

#                 detail="Invalid token scheme. Prefix must be 'Bearer'"

#             )

           

#         payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

#         user_id: str = payload.get("sub")

#         if user_id is None:

#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token mapping keys")

           

#     except (ValueError, JWTError):

#         raise HTTPException(

#             status_code=status.HTTP_401_UNAUTHORIZED,

#             detail="Token is expired, malformed, or invalid",

#         )



#     # Cast verification fallback chain

#     target_id = user_id

#     try:

#         uuid.UUID(str(user_id))

#     except ValueError:

#         try:

#             target_id = int(user_id)

#         except ValueError:

#             target_id = user_id



#     user = db.query(User).filter(User.id == target_id).first()

#     if user is None:

#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User account context not found")

       

#     return user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Extracts and validates JWT access token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your token has been expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise credentials_exception

    # Type verification mapping fallback chain
    target_id = user_id
    try:
        uuid.UUID(str(user_id))
    except ValueError:
        try:
            target_id = int(user_id)
        except ValueError:
            target_id = user_id

    user = db.query(User).filter(User.id == target_id).first()
    if user is None:
        raise credentials_exception

    return user





def require_role(allowed_roles: List[str]):

    def role_checker(current_user: User = Depends(get_current_user)) -> User:

        if current_user.role not in allowed_roles:

            raise HTTPException(

                status_code=status.HTTP_403_FORBIDDEN,

                detail=f"Access denied. Allowed roles: {allowed_roles}. Your role: {current_user.role}",

            )

        return current_user

    return role_checker 

