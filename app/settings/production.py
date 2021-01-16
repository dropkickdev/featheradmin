from .base import Base


class ProductionSettings(Base):
    DEBUG: bool = False
    SITE_URL: str = ''

    TESTDATA: str = 'This is production data'