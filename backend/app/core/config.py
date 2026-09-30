from pydantic_settings import BaseSettings
from pydantic import field_validator

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/db"
    NEON_AUTH_JWKS_URL: str = "https://example.com/.well-known/jwks.json"
    SECRET_KEY: str = "8Zrw7hFpbUqJ1Dk6Cq4Ltv9sYx2VnM5aR3eW8gKb0jNc7dHs6Pq1Xf4mUa9Bz2"
    LOCAL_AUTH_SECRET: str = "8Zrw7hFpbUqJ1Dk6Cq4Ltv9sYx2VnM5aR3eW8gKb0jNc7dHs6Pq1Xf4mUa9Bz2"
    LOCAL_AUTH_TOKEN_HOURS: int = 8
    APP_ENV: str = "development"
    ALLOWED_ORIGINS: list[str] = ["http://localhost:8501"]

    @field_validator("DATABASE_URL", mode="after")
    @classmethod
    def assemble_db_connection(cls, v: str) -> str:
        if v and v.startswith("postgresql://"):
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
        if v:
            # Map parameters for asyncpg
            v = v.replace("sslmode=", "ssl=")
            # Remove unsupported parameters
            if "channel_binding=" in v:
                import re
                v = re.sub(r'[&?]channel_binding=[^&]+', '', v)
        return v

    @property
    def is_neon_host(self) -> bool:
        return ".neon.tech" in self.DATABASE_URL

    @property
    def neon_host(self) -> str | None:
        if self.is_neon_host:
            import urllib.parse
            clean = self.DATABASE_URL.replace("postgresql+asyncpg://", "http://").replace("postgresql://", "http://")
            parsed = urllib.parse.urlparse(clean)
            return parsed.hostname
        return None

    @property
    def effective_db_url(self) -> str:
        """Returns rewritten database URL pointing through local WebSocket proxy if on Neon."""
        if self.is_neon_host:
            import urllib.parse
            parsed = urllib.parse.urlparse(self.DATABASE_URL)
            netloc_parts = parsed.netloc.split("@")
            userinfo = netloc_parts[0] if len(netloc_parts) > 1 else ""
            new_netloc = f"{userinfo}@127.0.0.1:5434"
            # Strip ssl query param since WSS handles encryption
            query = urllib.parse.parse_qs(parsed.query)
            query.pop("ssl", None)
            query.pop("sslmode", None)
            new_query = urllib.parse.urlencode(query, doseq=True)
            return urllib.parse.urlunparse((parsed.scheme, new_netloc, parsed.path, parsed.params, new_query, parsed.fragment))
        return self.DATABASE_URL

    class Config:
        env_file = ".env"

settings = Settings()
