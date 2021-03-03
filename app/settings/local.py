from .base import Base


class LocalSettings(Base):
    DEBUG: bool = True
    SITE_URL: str = 'http://localhost:9000'

    USERNAME_MIN: int = 4
    PASSWORD_MIN: int = 4
    
    ACCESS_TOKEN_EXPIRE: int = 3600 * 24 * 365
    REFRESH_TOKEN_EXPIRE: int = 3600
    REFRESH_TOKEN_CUTOFF: int = 10      # minutes
    # VERIFY_EMAIL_TTL: int = 180
    # RESET_PASSWORD_TTL: int = 180

    TESTDATA: str = 'This is local data'
    