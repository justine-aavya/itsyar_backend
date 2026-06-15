# from datetime import timedelta

# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session

# from app.database import get_db
# from app.models.user import User
# from app.schemas.auth import (
#     LoginRequest,
#     SignupRequest,
#     GoogleAuthRequest,
#     ForgotPasswordRequest,
#     ResetPasswordRequest,
#     TokenResponse,
#     UserResponse,
#     UserRole,
# )
# from app.core.security import (
#     hash_password,
#     verify_password,
#     create_access_token,
#     get_current_user,
#     require_role,
# )
# from app.core.config import settings

# router = APIRouter()


# # ─────────────────────────────────────────────
# # POST /api/auth/signup
# # ─────────────────────────────────────────────
# @router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
# def signup(request: SignupRequest, db: Session = Depends(get_db)):
#     # Check if user already exists
#     existing_user = db.query(User).filter(User.email == request.email).first()
#     if existing_user:
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail="An account with this email already exists",
#         )

#     # Create new user with role
#     new_user = User(
#         email=request.email,
#         hashed_password=hash_password(request.password),
#         full_name=request.full_name,
#         role=request.role.value,    # "Student", "Participant", "Mentor", or "Admin"
#     )
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)

#     # Generate token
#     access_token = create_access_token(data={"sub": new_user.id})

#     return TokenResponse(
#         access_token=access_token,
#         user=UserResponse.model_validate(new_user),
#     )


# # ─────────────────────────────────────────────
# # POST /api/auth/login
# # ─────────────────────────────────────────────
# @router.post("/login", response_model=TokenResponse)
# def login(request: LoginRequest, db: Session = Depends(get_db)):
#     # Find user by email
#     user = db.query(User).filter(User.email == request.email).first()
#     if not user or not user.hashed_password:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid email or password",
#         )

#     # Verify password
#     if not verify_password(request.password, user.hashed_password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid email or password",
#         )

#     # Token expiry based on "Remember me"
#     if request.remember_me:
#         expires = timedelta(days=settings.REMEMBER_ME_EXPIRE_DAYS)
#     else:
#         expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

#     access_token = create_access_token(data={"sub": user.id}, expires_delta=expires)

#     return TokenResponse(
#         access_token=access_token,
#         user=UserResponse.model_validate(user),
#     )


# # ─────────────────────────────────────────────
# # POST /api/auth/google  (Scaffolded)
# # ─────────────────────────────────────────────
# @router.post("/google", response_model=TokenResponse)
# def google_auth(request: GoogleAuthRequest, db: Session = Depends(get_db)):
#     """Google OAuth login/signup. Scaffolded — configure GOOGLE_CLIENT_ID to enable."""
#     raise HTTPException(
#         status_code=status.HTTP_501_NOT_IMPLEMENTED,
#         detail="Google OAuth is scaffolded. Configure GOOGLE_CLIENT_ID in .env to enable.",
#     )


# # ─────────────────────────────────────────────
# # POST /api/auth/forgot-password  (Scaffolded)
# # ─────────────────────────────────────────────
# @router.post("/forgot-password")
# def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
#     """Sends a password reset email. Scaffolded."""
#     return {"message": "If an account with that email exists, a reset link has been sent."}


# # ─────────────────────────────────────────────
# # POST /api/auth/reset-password  (Scaffolded)
# # ─────────────────────────────────────────────
# @router.post("/reset-password")
# def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
#     """Resets password using a token. Scaffolded."""
#     raise HTTPException(
#         status_code=status.HTTP_501_NOT_IMPLEMENTED,
#         detail="Password reset is scaffolded. Integrate email service to enable.",
#     )


# # ─────────────────────────────────────────────
# # GET /api/auth/me  (Any authenticated user)
# # ─────────────────────────────────────────────
# @router.get("/me", response_model=UserResponse)
# def get_me(current_user: User = Depends(get_current_user)):
#     """Returns the currently authenticated user."""
#     return UserResponse.model_validate(current_user)


# # ─────────────────────────────────────────────
# # GET /api/auth/users  (Admin only)
# # ─────────────────────────────────────────────
# @router.get("/users")
# def list_all_users(
#     current_user: User = Depends(require_role(["Admin"])),
#     db: Session = Depends(get_db),
# ):
#     """List all users. Admin only."""
#     users = db.query(User).all()
#     return {
#         "users": [UserResponse.model_validate(u) for u in users],
#         "count": len(users),
#     }

# from datetime import timedelta
# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session

# from jose import JWTError, jwt
# from app.schemas.auth import TokenResponse


# from app.database import get_db
# from app.models.user import User
# from app.schemas.auth import (
#     LoginRequest,
#     SignupRequest,
#     TokenResponse,
#     UserResponse, 
#     RefreshTokenRequest, 
#     ForgotPasswordRequest,
# )
# from app.core.security import (
#     hash_password,
#     verify_password,
#     create_access_token,
#     create_refresh_token, 
#     create_password_reset_token,
#     get_current_user,
# )
# from app.core.config import settings

# router = APIRouter()


# # ─────────────────────────────────────────────
# # POST /api/auth/signup
# # ─────────────────────────────────────────────
# @router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
# def signup(request: SignupRequest, db: Session = Depends(get_db)):
#     """
#     Sign Up — Join as Learner (Student) or Join Hackathon (Participant).
    
#     - Validates passwords match
#     - Validates terms accepted
#     - Validates learning_interest required for Students
#     - Checks email not already taken
#     - Hashes password and creates user
#     - Returns JWT token
#     """
#     # Check if email already exists
#     existing_user = db.query(User).filter(User.email == request.email).first()
#     if existing_user:
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail="An account with this email already exists",
#         )

#     # Create new user
#     new_user = User(
#         email=request.email,
#         hashed_password=hash_password(request.password),
#         full_name=request.full_name,
#         role=request.role.value,
#         learning_interest=request.learning_interest.value if request.learning_interest else None,
#     )
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)

#     # Create token
#     access_token = create_access_token(data={"sub": new_user.email, "role": new_user.role})
#     refresh_token = create_refresh_token(data={"sub": new_user.email})

#     return TokenResponse(
#         access_token=access_token,
#         refresh_token= refresh_token,  # 👈 Make sure this is spelled 'refresh_token'
#         token_type="bearer",
#         user=UserResponse.model_validate(new_user),
#     )


# # ─────────────────────────────────────────────
# # POST /api/auth/login
# # ─────────────────────────────────────────────
# @router.post("/login", response_model=TokenResponse)
# def login(request: LoginRequest, db: Session = Depends(get_db)):
#     """
#     Sign In — Email + Password + Remember Me.
#     """
#     user = db.query(User).filter(User.email == request.email).first()
#     if not user or not user.hashed_password:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid email or password",
#         )

#     if not verify_password(request.password, user.hashed_password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid email or password",
#         )

#     if request.remember_me:
#         expires = timedelta(days=settings.REMEMBER_ME_EXPIRE_DAYS)
#     else:
#         expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

#     access_token = create_access_token(data={"sub": user.email, "role": user.role})
#     refresh_token = create_refresh_token(data={"sub": user.email})

#     return TokenResponse(
#         access_token=access_token,
#         refresh_token=refresh_token,
#         token_type= "bearer",
#         user=UserResponse.model_validate(user)
#     )

# # ─────────────────────────────────────────────
# # POST /api/auth/refresh-token
# # ─────────────────────────────────────────────
# @router.post("/refresh-token", response_model=TokenResponse)
# def refresh_session(request: RefreshTokenRequest, db: Session = Depends(get_db)):
#     """Validates the refresh token and issues a fresh Access/Refresh pair."""
#     try:
#         payload = jwt.decode(request.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
#         user_id: str = payload.get("sub")
#         token_version: int = payload.get("version")
#         token_type: str = payload.get("type")

#         if token_type != "refresh" or user_id is None:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token mapping")
#     except JWTError:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired or invalid")

#     user = db.query(User).filter(User.id == user_id).first()
#     if not user or user.token_version != token_version:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session revoked or user invalid")

#     new_access = create_access_token(data={"sub": user.id})
#     new_refresh = create_refresh_token(data={"sub": user.id, "version": user.token_version})

#     return TokenResponse(
#         access_token=new_access,
#         refresh_token=new_refresh,
#         user=UserResponse.model_validate(user)
#     )

# # ─────────────────────────────────────────────
# # POST /api/auth/logout
# # ─────────────────────────────────────────────
# @router.post("/logout", status_code=status.HTTP_200_OK)
# def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     """Invalidates all of a user's active refresh tokens across all devices."""
#     current_user.token_version += 1
#     db.commit()
#     return {"message": "Logged out successfully from all concurrent sessions."}

# # ─────────────────────────────────────────────
# # POST /api/auth/forgot-password
# # ─────────────────────────────────────────────
# @router.post("/forgot-password", status_code=status.HTTP_200_OK)
# def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
#     """Generates a secure recovery signature context and prints it out to logs."""
#     user = db.query(User).filter(User.email == request.email).first()
#     if user:
#         reset_token = create_password_reset_token(user.id, user.hashed_password)
#         # Production: Wire email dispatcher. For now, print to console logs:
#         print(f"\n[RESET LINK HOOK]: http://localhost:3000/reset-password?token={reset_token}\n")

#     return {"message": "If that account exists, an email has been sent with recovery instructions."}

# # # ─────────────────────────────────────────────
# # # POST /api/auth/reset-password
# # # ─────────────────────────────────────────────
# # @router.post("/reset-password", status_code=status.HTTP_200_OK)
# # def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
# #     """Validates and processes password resets."""
# #     try:
# #         unverified_payload = jwt.get_unverified_claims(request.token)
# #         user_id = unverified_payload.get("sub")
# #     except JWTError:
# #         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Malformed payload string.")

# #     user = db.query(User).filter(User.id == user_id).first()
# #     if not user:
# #          raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token context invalid.")

# #     try:
# #         unique_secret = f"{settings.SECRET_KEY}{user.hashed_password}"
# #         jwt.decode(request.token, unique_secret, algorithms=[settings.ALGORITHM])
# #     except JWTError:
# #         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token expired or invalid.")

# #     user.hashed_password = hash_password(request.new_password)
# #     user.token_version += 1  # Forcing password change clears existing logged-in refresh tokens
# #     db.commit()

# #     return {"message": "Password updated successfully."}

# # ─────────────────────────────────────────────
# # GET /api/auth/me
# # ─────────────────────────────────────────────
# @router.get("/me", response_model=UserResponse)
# def get_me(current_user: User = Depends(get_current_user)):
#     """Get current user profile."""
#     return UserResponse.model_validate(current_user)

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.db.base import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    SignupRequest,
    TokenResponse,
    UserResponse, 
    RefreshTokenRequest, 
    ForgotPasswordRequest,
    ResetPasswordRequest
)
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token, 
    create_password_reset_token,
    get_current_user,
)
from app.core.config import settings

router = APIRouter()

# ─────────────────────────────────────────────
# POST /api/auth/signup
# ─────────────────────────────────────────────
@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """Registers a brand new user profile using fully lowercased runtime attributes."""
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    # Values are pre-processed to lowercase via Pydantic model field_validators
    new_user = User(
        email=request.email,
        hashed_password=hash_password(request.password),
        full_name=request.full_name,
        role=request.role,
        token_version=1
    )
    
    if hasattr(new_user, "learning_interest"):
        new_user.learning_interest = request.learning_interest

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Mint security credentials mapping strings explicitly
    access_token = create_access_token(data={"sub": str(new_user.id), "role": new_user.role})
    refresh_token = create_refresh_token(data={
        "sub": str(new_user.id),
        "type": "refresh",
        "version": new_user.token_version
    })

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,  
        token_type="bearer",
        user=UserResponse.model_validate(new_user),
    )

# ─────────────────────────────────────────────
# POST /api/auth/login
# ─────────────────────────────────────────────
@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticates user profile returns long-lived operational token maps."""
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    assigned_role = request.role or user.role

    access_token = create_access_token(
        data={"sub": str(user.id), "role": assigned_role}, 
        expires_delta=expires
    )
    
    refresh_token = create_refresh_token(
        data={
            "sub": str(user.id),
            "type": "refresh",
            "version": user.token_version
        }, 
        expires_delta=expires
    )

    # Validate output view model parameters mapping changes cleanly
    response_user = UserResponse.model_validate(user)
    response_user.role = assigned_role

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=response_user  # 👈 FIXED: Passes the runtime mutated schema model directly
    )

# ─────────────────────────────────────────────
# POST /api/auth/refresh-token
# ─────────────────────────────────────────────
@router.post("/refresh-token", response_model=TokenResponse)
def refresh_session(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Decodes system refresh tokens to issue a fresh access/refresh pair."""
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
    new_refresh = create_refresh_token(data={
        "sub": str(user.id), 
        "type": "refresh",
        "version": user.token_version
    })

    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )

# ─────────────────────────────────────────────
# POST /api/auth/logout
# ─────────────────────────────────────────────
@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Increments user session values to invalidate active tokens globally."""
    current_user.token_version += 1
    db.commit()
    return {"message": "Logged out successfully from all concurrent sessions."}

# ─────────────────────────────────────────────
# POST /api/auth/forgot-password
# ─────────────────────────────────────────────
@router.post("/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Generates password recovery signature links for staging inspection."""
    user = db.query(User).filter(User.email == request.email).first()
    if user:
        reset_token = create_password_reset_token(str(user.id), user.hashed_password)
        print(f"\n[RESET LINK HOOK]: http://localhost:3000/reset-password?token={reset_token}\n")

    return {"message": "If that account exists, an email has been sent with recovery instructions."}

# ─────────────────────────────────────────────
# POST /api/auth/reset-password
# ─────────────────────────────────────────────
@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Validates unverified tokens and modifies corresponding row hashes."""
    try:
        unverified_payload = jwt.get_unverified_claims(request.token)
        user_id = unverified_payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Malformed payload string.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token context invalid.")

    try:
        unique_secret = f"{settings.SECRET_KEY}{user.hashed_password}"
        jwt.decode(request.token, unique_secret, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token expired or invalid.")

    user.hashed_password = hash_password(request.new_password)
    user.token_version += 1  
    db.commit()

    return {"message": "Password updated successfully."}

# ─────────────────────────────────────────────
# GET /api/auth/me
# ─────────────────────────────────────────────
@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Returns profile structure for the currently authenticated bearer token."""
    return UserResponse.model_validate(current_user)