# # from pydantic import BaseModel, EmailStr
# # from typing import Optional
# # from enum import Enum


# # class UserRole(str, Enum):
# #     STUDENT = "Student"
# #     PARTICIPANT = "Participant"
# #     MENTOR = "Mentor"
# #     ADMIN = "Admin"


# # # --- Request Schemas ---

# # class LoginRequest(BaseModel):
# #     email: EmailStr
# #     password: str
# #     remember_me: bool = False


# # class SignupRequest(BaseModel):
# #     email: EmailStr
# #     password: str
# #     full_name: Optional[str] = None
# #     role: UserRole = UserRole.STUDENT


# # class GoogleAuthRequest(BaseModel):
# #     google_token: str


# # class ForgotPasswordRequest(BaseModel):
# #     email: EmailStr


# # class ResetPasswordRequest(BaseModel):
# #     token: str
# #     new_password: str


# # # --- Response Schemas ---

# # class UserResponse(BaseModel):
# #     id: str
# #     email: str
# #     full_name: Optional[str] = None
# #     role: str

# #     class Config:
# #         from_attributes = True


# # class TokenResponse(BaseModel):
# #     access_token: str
# #     token_type: str = "bearer"
# #     user: UserResponse

# # auth.py
# from pydantic import BaseModel, EmailStr, ConfigDict, field_validator, model_validator, ValidationInfo
# from typing import Optional
# from enum import Enum

# class UserRole(str, Enum):
#     STUDENT = "Student"
#     PARTICIPANT = "Participant"
#     MENTOR = "Mentor"
#     ADMIN = "Admin"

# class LearningInterest(str, Enum):
#     DATA_SCIENCE = "Data Science"
#     AI_ML = "AI & Machine Learning"
#     WEB_DEVELOPMENT = "Web Development"
#     CLOUD_COMPUTING = "Cloud Computing"
#     CYBERSECURITY = "Cybersecurity"
#     DEVOPS = "DevOps"
#     MOBILE_DEVELOPMENT = "Mobile Development"
#     OTHER = "Other"

# # ─────────────────────────────────────────────
# # Requests
# # ─────────────────────────────────────────────

# class SignupRequest(BaseModel):
#     full_name: str
#     email: EmailStr
#     password: str
#     confirm_password: str
#     role: Optional[str] = "Student"
#     learning_interest: Optional[LearningInterest] = "Data Science"  # Required only for Students

#     @field_validator("full_name", mode="before")
#     @classmethod
#     def clean_full_name(cls, value: str) -> str:
#         if isinstance(value, str):
#             return value.strip()  # Cleans whitespace trailing edges without breaking casing
#         return value

#     @field_validator("email", mode="before")
#     @classmethod
#     def transform_to_lowercase(cls, value: str) -> str:
#         if isinstance(value, str):
#             return value.strip().lower()
#         return value

#     @field_validator("confirm_password")
#     @classmethod
#     def passwords_match(cls, v: str, info: ValidationInfo):
#         if "password" in info.data and v != info.data["password"]:
#             raise ValueError("Passwords do not match")
#         return v

#     @model_validator(mode="after")
#     def verify_passwords_match(self) -> "SignupRequest":
#         if self.password != self.confirm_password:
#             raise ValueError("Passwords do not match.")
#         return self

#     @field_validator("learning_interest")
#     @classmethod
#     def learner_needs_interest(cls, v, info: ValidationInfo):
#         """
#         Ensures a course learning interest selection is provided 
#         whether the incoming role is 'Student' OR 'Participant'.
#         """
#         if "role" in info.data and v is None:
#             if info.data["role"] in [UserRole.STUDENT, UserRole.PARTICIPANT]:
#                 raise ValueError("Learning Interest course selection is required to complete enrollment.")
#         return v


# class LoginRequest(BaseModel):
#     email: EmailStr
#     password: str
#     role: Optional[str] = "Student"

#     @field_validator("email", mode="before")
#     @classmethod
#     def transform_login_to_lowercase(cls, value: str) -> str:
#         if isinstance(value, str):
#             return value.strip().lower()
#         return value
    
#     model_config = ConfigDict(extra="ignore")


# class RefreshTokenRequest(BaseModel):
#     refresh_token: str


# class ForgotPasswordRequest(BaseModel):
#     email: EmailStr


# class ResetPasswordRequest(BaseModel):
#     token: str
#     new_password: str
#     confirm_new_password: str

#     @model_validator(mode="after")
#     def passwords_match_verification(self) -> "ResetPasswordRequest":
#         if self.new_password != self.confirm_new_password:
#             raise ValueError("Passwords do not match")
#         return self


# # ─────────────────────────────────────────────
# # Responses
# # ─────────────────────────────────────────────

# class UserResponse(BaseModel):
#     id: str
#     email: str
#     full_name: str
#     role: str
#     learning_interest: Optional[str] = None

#     model_config = ConfigDict(from_attributes=True)


# class TokenResponse(BaseModel):
#     access_token: str
#     refresh_token: str
#     token_type: str = "bearer"
#     user: UserResponse



from pydantic import BaseModel, EmailStr, ConfigDict, field_validator, model_validator, ValidationInfo

from typing import Optional

from enum import Enum





class UserRole(str, Enum):

    STUDENT = "Student"

    PARTICIPANT = "Participant"

    MENTOR = "Mentor"

    ADMIN = "Admin"





class LearningInterest(str, Enum):

    DATA_SCIENCE = "Data Science"

    AI_ML = "AI & Machine Learning"

    WEB_DEVELOPMENT = "Web Development"

    CLOUD_COMPUTING = "Cloud Computing"

    CYBERSECURITY = "Cybersecurity"

    DEVOPS = "DevOps"

    MOBILE_DEVELOPMENT = "Mobile Development"

    OTHER = "Other"





# ─────────────────────────────────────────────

# Requests

# ─────────────────────────────────────────────



class SignupRequest(BaseModel):

    full_name: str

    email: EmailStr

    password: str

    confirm_password: str

    role: Optional[str] = "Student"

    learning_interest: Optional[LearningInterest] = "Data Science"  # Required only for Students



    @field_validator("full_name", "email", mode="before")

    @classmethod

    def transform_to_lowercase(cls, value: str) -> str:

        if isinstance(value, str):

            return value.strip().lower()

        return value



    #  FIXED: Swapped to @field_validator and added ValidationInfo

    @field_validator("confirm_password")

    @classmethod

    def passwords_match(cls, v: str, info: ValidationInfo):

        if "password" in info.data and v != info.data["password"]:

            raise ValueError("Passwords do not match")

        return v



    @model_validator(mode="after")

    def verify_passwords_match(self):

        if self.password != self.confirm_password:

            raise ValueError("Passwords do not match.")

        return self



    #  FIXED: Swapped to @field_validator and added ValidationInfo

    @field_validator("learning_interest")

    @classmethod

    def learner_needs_interest(cls, v, info: ValidationInfo):

        """

        Ensures a course learning interest selection is provided

        whether the incoming role is 'Student' OR 'Participant'.

        """

        if "role" in info.data and v is None:

            # Check if the chosen role is part of our active signup enrollment tier

            if info.data["role"] in [UserRole.STUDENT, UserRole.PARTICIPANT]:

                raise ValueError("Learning Interest course selection is required to complete enrollment.")

        return v





class LoginRequest(BaseModel):

    email: EmailStr

    password: str

    # remember_me: bool = False

    role: Optional[str] = "Student"



    @field_validator("email", mode="before")

    @classmethod

    def transform_login_to_lowercase(cls, value: str) -> str:

        if isinstance(value, str):

            return value.strip().lower()

        return value

   

    model_config = ConfigDict(extra="ignore")



class RefreshTokenRequest(BaseModel):

    refresh_token: str





class ForgotPasswordRequest(BaseModel):

    email: EmailStr





class ResetPasswordRequest(BaseModel):

    token: str

    new_password: str

    confirm_new_password: str



    @model_validator(mode="after")

    def passwords_match_verification(self) -> "ResetPasswordRequest":

        if self.new_password != self.confirm_new_password:

            raise ValueError("Passwords do not match")

        return self





# ─────────────────────────────────────────────

# Responses

# ─────────────────────────────────────────────



class UserResponse(BaseModel):

    id: str

    email: str

    full_name: str

    role: str

    learning_interest: Optional[str] = None



    model_config = ConfigDict(from_attributes=True)





class TokenResponse(BaseModel):

    access_token: str

    refresh_token: str

    token_type: str = "bearer"

    user: UserResponse
