
# from datetime import timedelta

# from fastapi import APIRouter, Depends, HTTPException, status

# from sqlalchemy.orm import Session

# from jose import JWTError, jwt



# from app.db.session import get_db

# from app.models.user import User

# from app.api.deps import get_current_user

# from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, create_password_reset_token

# from app.core.config import settings

# from app.models.auth.schemas import (

#     LoginRequest, SignupRequest, RefreshTokenRequest,

#     ForgotPasswordRequest, ResetPasswordRequest, TokenResponse, UserResponse

# )
# from app.integrations.palantir import foundry_service




# router = APIRouter()



# @router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)

# def signup(request: SignupRequest, db: Session = Depends(get_db)):

#     existing_user = db.query(User).filter(User.email == request.email).first()

#     if existing_user:

#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists")



#     new_user = User(

#         email=request.email,

#         hashed_password=hash_password(request.password),

#         full_name=request.full_name,

#         role=request.role,

#         learning_interest=request.learning_interest.value if request.learning_interest else None,

#         token_version=1

#     )

#     db.add(new_user)

#     db.commit()

#     db.refresh(new_user)

#         # Push to Foundry
#     foundry_service.push_user_to_foundry(
#         user_id=str(new_user.id),
#         email=new_user.email,
#         full_name=new_user.full_name,
#         role=new_user.role or "Student",
#         learning_interest=new_user.learning_interest or "",
#     )




#     access_token = create_access_token(data={"sub": str(new_user.id), "role": new_user.role})

#     refresh_token = create_refresh_token(data={"sub": str(new_user.id), "type": "refresh", "version": new_user.token_version})



#     return TokenResponse(

#         access_token=access_token,

#         refresh_token=refresh_token,

#         user=UserResponse.model_validate(new_user)

#     )



# @router.post("/login", response_model=TokenResponse)

# def login(request: LoginRequest, db: Session = Depends(get_db)):

#     user = db.query(User).filter(User.email == request.email).first()

#     if not user or not user.hashed_password or not verify_password(request.password, user.hashed_password):

#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")



#     expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

#     #assigned_role = request.role or user.role
#     assigned_role = user.role




#     access_token = create_access_token(data={"sub": str(user.id), "role": assigned_role}, expires_delta=expires)

#     refresh_token = create_refresh_token(data={"sub": str(user.id), "type": "refresh", "version": user.token_version}, expires_delta=expires)



#     response_user = UserResponse.model_validate(user)

#     response_user.role = assigned_role



#     return TokenResponse(access_token=access_token, refresh_token=refresh_token, user=response_user)



# @router.post("/refresh-token", response_model=TokenResponse)

# def refresh_session(request: RefreshTokenRequest, db: Session = Depends(get_db)):

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



#     new_access = create_access_token(data={"sub": str(user.id), "role": user.role})

#     new_refresh = create_refresh_token(data={"sub": str(user.id), "type": "refresh", "version": user.token_version})

#     return TokenResponse(access_token=new_access, refresh_token=new_refresh, user=UserResponse.model_validate(user))



# @router.post("/forgot-password")

# def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):

#     user = db.query(User).filter(User.email == request.email).first()

#     if user:

#         reset_token = create_password_reset_token(str(user.id), user.hashed_password)

#         print(f"\n[RESET LINK]: http://localhost:3000/reset-password?token={reset_token}\n")

#     return {"message": "If that account exists, an email has been sent with recovery instructions."}



# @router.post("/reset-password")

# def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):

#     try:

#         unverified_payload = jwt.get_unverified_claims(request.token)

#         user_id = unverified_payload.get("sub")

#     except JWTError:

#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Malformed token.")

#     user = db.query(User).filter(User.id == user_id).first()

#     if not user:

#          raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token context.")

#     try:

#         jwt.decode(request.token, f"{settings.SECRET_KEY}{user.hashed_password}", algorithms=[settings.ALGORITHM])

#     except JWTError:

#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token expired or invalid.")



#     user.hashed_password = hash_password(request.new_password)

#     user.token_version += 1  

#     db.commit()

#     return {"message": "Password updated successfully."}



from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from app.core.config import settings
from app.models.auth.schemas import GoogleAuthRequest

    
from app.db.session import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, create_password_reset_token
from app.core.config import settings
from app.models.auth.schemas import (
    LoginRequest, SignupRequest, RefreshTokenRequest,
    ForgotPasswordRequest, ResetPasswordRequest, TokenResponse, UserResponse
)
from app.integrations.palantir import foundry_service
from app.integrations.google.oauth import verify_google_token



router = APIRouter()


def error_response(status_code: int, message: str):
    """Standard error response: {"error": {"data": {"message": "..."}}}"""
    return JSONResponse(
        status_code=status_code,
        content={"error": {"data": {"message": message}}}
    )


# ═══════════════════════════════════════════════════════════════
# GOOGLE OAUTH — Sign In / Sign Up with Google
# ═══════════════════════════════════════════════════════════════

@router.post("/google", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def google_auth(request: GoogleAuthRequest, db: Session = Depends(get_db)):
    """
    Authenticate with Google. Handles both signup and login:
    - If email exists → login (auto-link accounts)
    - If email doesn't exist → create new user (signup)
    
    Frontend sends the Google ID token obtained from Google Sign-In button.
    """
    try:
        # Step 1: Verify the Google ID token
        # This checks the token is valid, not expired, and issued by Google
        google_info = id_token.verify_oauth2_token(
            request.token,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )

        # Step 2: Extract user info from Google
        google_email = google_info.get("email", "").strip().lower()
        google_name = google_info.get("name", "")
        google_sub = google_info.get("sub", "")  # Google's unique user ID

        if not google_email:
            return error_response(400, "Google account has no email address")

        # Step 3: Check if user already exists (by email)
        user = db.query(User).filter(User.email == google_email).first()

        if user:
            # ─── EXISTING USER: Login + link Google if not already ─────
            if user.auth_provider == "local":
                # User signed up with email/password, now using Google too
                user.auth_provider = "both"
                db.commit()

            assigned_role = user.role

        else:
            # ─── NEW USER: Signup via Google ──────────────────────────
            user = User(
                email=google_email,
                hashed_password=None,  # No password for Google users
                full_name=google_name,
                role=request.role,
                learning_interest=request.learning_interest.value if request.learning_interest else "Data Science",
                auth_provider="google",
                token_version=1
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            assigned_role = user.role

            # Push to Foundry
            foundry_service.push_user_to_foundry(
                user_id=str(user.id),
                email=user.email,
                full_name=user.full_name,
                role=user.role,
                learning_interest="",
            )

        # Step 4: Generate JWT tokens
        access_token = create_access_token(data={"sub": str(user.id), "role": assigned_role})
        refresh_token = create_refresh_token(data={"sub": str(user.id), "type": "refresh", "version": user.token_version})

        # Step 5: Return response
        response_user = UserResponse.model_validate(user)
        response_user.role = assigned_role

        return TokenResponse(
            success=True,
            access_token=access_token,
            refresh_token=refresh_token,
            user=response_user
        )

    except ValueError as e:
        # Invalid Google token
        return error_response(401, f"Invalid Google token: {str(e)}")
    except Exception as e:
        return error_response(500, f"Google authentication failed: {str(e)}")


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        return error_response(409, "An account with this email already exists")

    new_user = User(
        email=request.email,
        hashed_password=hash_password(request.password),
        full_name=request.full_name,
        role=request.role,
        learning_interest=request.learning_interest.value if request.learning_interest else "Data Science",
        token_version=1
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Push to Foundry
    foundry_service.push_user_to_foundry(
        user_id=str(new_user.id),
        email=new_user.email,
        full_name=new_user.full_name,
        role=new_user.role or "Student",
        learning_interest=new_user.learning_interest or "",
    )

    access_token = create_access_token(data={"sub": str(new_user.id), "role": new_user.role})
    refresh_token = create_refresh_token(data={"sub": str(new_user.id), "type": "refresh", "version": new_user.token_version})

    return TokenResponse(
        success=True,
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(new_user)
    )


# @router.post("/login", response_model=TokenResponse)
# def login(request: LoginRequest, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.email == request.email).first()
#     if not user or not user.hashed_password or not verify_password(request.password, user.hashed_password):
#         return error_response(401, "Invalid email or password")

#     expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
#     assigned_role = user.role

#     access_token = create_access_token(data={"sub": str(user.id), "role": assigned_role}, expires_delta=expires)
#     refresh_token = create_refresh_token(data={"sub": str(user.id), "type": "refresh", "version": user.token_version}, expires_delta=expires)

#     response_user = UserResponse.model_validate(user)
#     response_user.role = assigned_role

#     return TokenResponse(success=True, access_token=access_token, refresh_token=refresh_token, user=response_user)

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()

    # Check if user exists
    if not user:
        return error_response(401, "Invalid email or password")

    # Check if this is a Google-only user (no password set)
    if not user.hashed_password and user.auth_provider == "google":
        return error_response(403, "This account uses Google Sign-In. Please login with Google.")

    # Verify password
    if not user.hashed_password or not verify_password(request.password, user.hashed_password):
        return error_response(401, "Invalid email or password")

    # Use stored role
    assigned_role = user.role

    # Validate that the requested role matches the stored role (if provided)
    if request.role and request.role.lower() != user.role.lower():
        return error_response(403, f"Your account is registered as '{user.role}'. Cannot login as '{request.role}'.")

    expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # Create tokens with role included
    access_token = create_access_token(data={"sub": str(user.id), "role": assigned_role}, expires_delta=expires)
    refresh_token = create_refresh_token(data={"sub": str(user.id), "type": "refresh", "version": user.token_version}, expires_delta=expires)

    # Build response with role
    response_user = UserResponse.model_validate(user)
    response_user.role = assigned_role

    return TokenResponse(success=True, access_token=access_token, refresh_token=refresh_token, user=response_user)



@router.post("/refresh-token", response_model=TokenResponse)
def refresh_session(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(request.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        token_version: int = payload.get("version")
        token_type: str = payload.get("type")
        if token_type != "refresh" or user_id is None:
            return error_response(401, "Invalid token mapping")
    except JWTError:
        return error_response(401, "Refresh token expired or invalid")

    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.token_version != token_version:
        return error_response(401, "Session revoked or user invalid")

    new_access = create_access_token(data={"sub": str(user.id), "role": user.role})
    new_refresh = create_refresh_token(data={"sub": str(user.id), "type": "refresh", "version": user.token_version})
    return TokenResponse(success=True, access_token=new_access, refresh_token=new_refresh, user=UserResponse.model_validate(user))


@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if user:
        reset_token = create_password_reset_token(str(user.id), user.hashed_password)
        print(f"\n[RESET LINK]: http://localhost:3000/reset-password?token={reset_token}\n")
    return {"success": True, "message": "If that account exists, an email has been sent with recovery instructions."}


@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    try:
        unverified_payload = jwt.get_unverified_claims(request.token)
        user_id = unverified_payload.get("sub")
    except JWTError:
        return error_response(400, "Malformed token.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return error_response(400, "Invalid token context.")

    try:
        jwt.decode(request.token, f"{settings.SECRET_KEY}{user.hashed_password}", algorithms=[settings.ALGORITHM])
    except JWTError:
        return error_response(400, "Token expired or invalid.")

    user.hashed_password = hash_password(request.new_password)
    user.token_version += 1
    db.commit()
    return {"success": True, "message": "Password updated successfully."}
 