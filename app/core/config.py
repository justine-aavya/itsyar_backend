# from pydantic_settings import BaseSettings, SettingsConfigDict

# from typing import Optional



# class Settings(BaseSettings):

#     # Core Application Properties

#     DATABASE_URL: str

#     SECRET_KEY: str

#     ALGORITHM: str = "HS256"

#     ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

#     REMEMBER_ME_EXPIRE_DAYS: int = 7

   

#     # FOUNDRY PROPERTIES (With Snake and Camel Variable Fallbacks)

#     FOUNDRY_URL: Optional[str] = None

   

#     # Client ID Fallbacks

#     CLIENT_ID: Optional[str] = None

#     FOUNDRY_CLIENT_ID: Optional[str] = None

   

#     # Client Secret Fallbacks

#     CLIENT_SECRET: Optional[str] = None

#     FOUNDRY_CLIENT_SECRET: Optional[str] = None

#     foundry_client_secret: Optional[str] = None

   

#     # Ontology RID Fallbacks

#     ONTOLOGY_RID: Optional[str] = None

#     FOUNDRY_ONTOLOGY_RID: Optional[str] = None

#     foundry_ontology_rid: Optional[str] = None



#     model_config = SettingsConfigDict(

#         env_file=".env",

#         env_file_encoding="utf-8",

#         extra="ignore",

#         case_sensitive=False

#     )



# settings = Settings()

#########################################################################################################################

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    # Core
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REMEMBER_ME_EXPIRE_DAYS: int = 7

    # Google OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None

    # Foundry
    FOUNDRY_URL: Optional[str] = None
    CLIENT_ID: Optional[str] = None
    FOUNDRY_CLIENT_ID: Optional[str] = None
    CLIENT_SECRET: Optional[str] = None
    FOUNDRY_CLIENT_SECRET: Optional[str] = None
    foundry_client_secret: Optional[str] = None
    ONTOLOGY_RID: Optional[str] = None
    FOUNDRY_ONTOLOGY_RID: Optional[str] = None
    foundry_ontology_rid: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False
    )


settings = Settings()
