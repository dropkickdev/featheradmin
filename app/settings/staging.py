from .production import Base


class StagingSettings(Base):
    SITE_URL: str = 'http://FOOBAR'

    TESTDATA: str = 'This is staging data'