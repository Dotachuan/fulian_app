from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "foundation_donation"

    SECRET_KEY: str = "change_this_secret"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    MEMBER_ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080

    UPLOAD_DIR: str = "./uploads"
    PUBLIC_ASSET_ORIGIN: str = "https://api.fulian520.com"
    MEMBER_SMS_DEBUG_RETURN_CODE: bool = True
    WECHAT_MINIAPP_APPID: str = ""
    WECHAT_MINIAPP_SECRET: str = ""
    WECHAT_API_TIMEOUT_SECONDS: int = 10

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        )

    class Config:
        env_file = ".env"


settings = Settings()
