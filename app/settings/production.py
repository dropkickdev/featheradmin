from .base import Base


class ProductionSettings(Base):
    DEBUG: bool = False
    SITE_URL: str = 'http://FOOBAR'

    TESTDATA: str = 'This is production data'