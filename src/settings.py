from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseSettingsWithConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class PostgresSettings(BaseSettingsWithConfig):
    model_config = SettingsConfigDict(env_prefix="postgres_")

    host:   str
    port:   int
    user:   str
    passwd: str
    name:   str

    @property
    def dsn(self) -> str:
        return f"postgresql+psycopg2://{self.user}:{self.passwd}@{self.host}:{self.port}"


class JWTSettings(BaseSettingsWithConfig):
    model_config = SettingsConfigDict(env_prefix="jwt_")

    algorithm:  str
    secret_key: str

    access_token_expire_minutes: int = 15
    refresh_token_expire_days:   int = 30


class MailSettings(BaseSettingsWithConfig):
    model_config = SettingsConfigDict(env_prefix="mail_")

    server: str
    port:   int
    user:   str
    passwd: str


class RedisSettings(BaseSettingsWithConfig):
    model_config = SettingsConfigDict(env_prefix="redis_")

    host: str
    port: int


class CloudinarySettings(BaseSettingsWithConfig):
    model_config = SettingsConfigDict(env_prefix="cloudinary_")

    name: str
    api_key: str
    api_secret: str


class Settings(BaseSettingsWithConfig):
    jwt: JWTSettings = JWTSettings()
    mail: MailSettings = MailSettings()
    postgres: PostgresSettings = PostgresSettings()
    redis: RedisSettings = RedisSettings()
    cloudinary: CloudinarySettings = CloudinarySettings()


settings = Settings()
