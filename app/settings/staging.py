from .production import Base


class StagingSettings(Base):
    SITE_URL: str = ''

    TESTDATA: str = 'This is staging data'