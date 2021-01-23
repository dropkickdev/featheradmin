from .base import Base


class LocalSettings(Base):
    DEBUG: bool = True
    SITE_URL: str = 'http://localhost:9000'

    USERNAME_MIN: int = 4
    PASSWORD_MIN: int = 4
    
    ACCESS_TOKEN_EXPIRE: int = 15
    REFRESH_TOKEN_EXPIRE: int = 3600
    REFRESH_TOKEN_CUTOFF: int = 10      # minutes

    TESTDATA: str = 'This is local data'
    