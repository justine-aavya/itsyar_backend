from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.db.session import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, create_password_reset_token
from app.core.config import settings
from app.models.auth.schemas import (
    LoginRequest, SignupRequest, RefreshTokenRequest, 
    ForgotPasswordRequest, ResetPasswordRequest, TokenResponse, UserResponse
)

router = APIRouter()

@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists")

    new_user = User(
        email=request.email,
        hashed_password=hash_password(request.password),
        full_name=request.full_name,
        role=request.role,
        learning_interest=request.learning_interest.value if request.learning_interest else None,
        token_version=1
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token(data={"sub": str(new_user.id), "role": new_user.role})
    refresh_token = create_refresh_token(data={"sub": str(new_user.id), "type": "refresh", "version": new_user.token_version})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(new_user)
    )

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not user.hashed_password or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    assigned_role = request.role or user.role

    access_token = create_access_token(data={"sub": str(user.id), "role": assigned_role}, expires_delta=expires)
    refresh_token = create_refresh_token(data={"sub": str(user.id), "type": "refresh", "version": user.token_version}, expires_delta=expires)

    response_user = UserResponse.model_validate(user)
    response_user.role = assigned_role

    return TokenResponse(access_token=access_token, refresh_token=refresh_token, user=response_user)

@router.post("/refresh-token", response_model=TokenResponse)
def refresh_session(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(request.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        token_version: int = payload.get("version")
        token_type: str = payload.get("type")
        if token_type != "refresh" or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token mapping")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired or invalid")

    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.token_version != token_version:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session revoked or user invalid")

    new_access = create_access_token(data={"sub": str(user.id), "role": user.role})
    new_refresh = create_refresh_token(data={"sub": str(user.id), "type": "refresh", "version": user.token_version})
    return TokenResponse(access_token=new_access, refresh_token=new_refresh, user=UserResponse.model_validate(user))

@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if user:
        reset_token = create_password_reset_token(str(user.id), user.hashed_password)
        print(f"\n[RESET LINK]: http://localhost:3000/reset-password?token={reset_token}\n")
    return {"message": "If that account exists, an email has been sent with recovery instructions."}

@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    try:
        unverified_payload = jwt.get_unverified_claims(request.token)
        user_id = unverified_payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Malformed token.")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token context.")
    try:
        jwt.decode(request.token, f"{settings.SECRET_KEY}{user.hashed_password}", algorithms=[settings.ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token expired or invalid.")

    user.hashed_password = hash_password(request.new_password)
    user.token_version += 1  
    db.commit()
    return {"message": "Password updated successfully."}