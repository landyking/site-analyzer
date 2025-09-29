import secrets
import warnings
from typing import Annotated, Any, Literal
from pathlib import Path

from pydantic import (
    AnyUrl,
    BeforeValidator,
    EmailStr,
    HttpUrl,
    MySQLDsn,
    computed_field,
    model_validator,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


def parse_abs_path(v: Any) -> Path | None:
    """Ensure the provided value is an absolute filesystem path.

    Accepts strings or Path instances. Expands '~'. Raises ValueError if not absolute.
    """
    if v in (None, ""):
        return None
    if isinstance(v, (str, Path)):
        p = Path(v).expanduser()
        if not p.is_absolute():
            raise ValueError(f"Path must be absolute: {p}")
        return p
    raise ValueError(f"Invalid path value: {v!r}")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Use top level .env file (one level above ./backend/)
        # env_file="../.env",
        env_file=["../.env", "../.env.local","../.env.production"],
        env_ignore_empty=True,
        extra="ignore",
    )
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    FRONTEND_HOST: str = "http://localhost:5173"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]

    PROJECT_NAME: str
    SENTRY_DSN: HttpUrl | None = None
    MYSQL_SERVER: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_DB: str = "site_analyzer"

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str

    # Absolute paths to input and output data directories (configured via env/.env)
    INPUT_DATA_DIR: Annotated[Path, BeforeValidator(parse_abs_path)]
    OUTPUT_DATA_DIR: Annotated[Path, BeforeValidator(parse_abs_path)]

    STORAGE_ENABLED: bool = False
    STORAGE_ENDPOINT: str
    STORAGE_ACCESS_KEY: str
    STORAGE_SECRET_KEY: str
    STORAGE_BUCKET: str
    STORAGE_REGION: str
    STORAGE_SIGN_EXPIRE_SECONDS: int = 3600  # 1 hour

    RELEASE_READ_ONLY: bool = False
    RELEASE_ALLOW_REGISTRATION: bool = True

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> MySQLDsn:
        return MultiHostUrl.build(
            scheme="mysql+pymysql",
            username=self.MYSQL_USER,
            password=self.MYSQL_PASSWORD,
            host=self.MYSQL_SERVER,
            port=self.MYSQL_PORT,
            path=self.MYSQL_DB,
        )

    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: EmailStr | None = None
    EMAILS_FROM_NAME: EmailStr | None = None

    @model_validator(mode="after")
    def _set_default_emails_from(self) -> Self:
        if not self.EMAILS_FROM_NAME:
            self.EMAILS_FROM_NAME = self.PROJECT_NAME
        return self

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48

    @computed_field  # type: ignore[prop-decorator]
    @property
    def emails_enabled(self) -> bool:
        return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL)

    EMAIL_TEST_USER: EmailStr = "test@example.com"
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str

    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        if value == "changethis":
            message = (
                f'The value of {var_name} is "changethis", '
                "for security, please change it, at least for deployments."
            )
            if self.ENVIRONMENT == "local":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        self._check_default_secret("MYSQL_PASSWORD", self.MYSQL_PASSWORD)
        self._check_default_secret(
            "FIRST_SUPERUSER_PASSWORD", self.FIRST_SUPERUSER_PASSWORD
        )

        return self


settings = Settings()  # type: ignore
# print(settings.INPUT_DATA_DIR, settings.OUTPUT_DATA_DIR)
# print(settings.GOOGLE_CLIENT_ID, settings.GOOGLE_CLIENT_SECRET)