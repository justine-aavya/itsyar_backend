# from pydantic import BaseModel, EmailStr, ConfigDict, field_validator, model_validator, ValidationInfo, Field

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



# class SignupRequest(BaseModel):
#     full_name: str = Field(alias="fullName")
#     email: EmailStr
#     password: str
#     confirm_password: str = Field(alias="confirmPassword")
#     role: Optional[str] = Field(default="Student", alias="userType")
#     #learning_interest: Optional[LearningInterest] = Field(default="Data Science", alias="interest")
#     accept_terms: bool = Field(default=True, alias="acceptTerms")

#     class Config:
#         populate_by_name = True  # Accept both camelCase and snake_case

#     @field_validator("full_name", "email", mode="before")
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
#     def verify_passwords_match(self):
#         if self.password != self.confirm_password:
#             raise ValueError("Passwords do not match.")
#         if not self.accept_terms:
#             raise ValueError("You must accept the terms and conditions.")
#         return self

#     # @field_validator("learning_interest")
#     # @classmethod
#     # def learner_needs_interest(cls, v, info: ValidationInfo):
#     #     if "role" in info.data and v is None:
#     #         if info.data["role"] in [UserRole.STUDENT, UserRole.PARTICIPANT]:
#     #             raise ValueError("Learning Interest course selection is required to complete enrollment.")
#     #     return v




# class LoginRequest(BaseModel):

#     email: EmailStr

#     password: str

#     #role: Optional[str] = "Student"



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

from pydantic import BaseModel, EmailStr, ConfigDict, field_validator, model_validator, ValidationInfo, Field
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


class GoogleAuthRequest(BaseModel):
    """Frontend sends the Google ID token after user signs in with Google."""
    token: str  # Google ID token from frontend
    role: Optional[str] = Field(default="Student", alias="userType")
    learning_interest: Optional[str] = Field(default=None, alias="interest")

    model_config = ConfigDict(populate_by_name=True)


class SignupRequest(BaseModel):
    full_name: str = Field(alias="fullName")
    email: EmailStr
    password: str
    confirm_password: str = Field(alias="confirmPassword")
    role: Optional[str] = Field(default="Student", alias="role")
    learning_interest: Optional[LearningInterest] = Field(default=None, alias="interest")  
    accept_terms: bool = Field(alias="acceptTerms")

    class Config:
        populate_by_name = True

    @field_validator("full_name", "email", mode="before")
    @classmethod
    def transform_to_lowercase(cls, value: str) -> str:
        if isinstance(value, str):
            return value.strip().lower()
        return value

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
        if not self.accept_terms:
            raise ValueError("You must accept the terms and conditions.")
        return self


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    role: Optional[str] = Field(default=None, alias="role")  # Optional: login as specific role

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


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    learning_interest: Optional[str] = None
    auth_provider: Optional[str] = "local"  

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    success: bool = True
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse
