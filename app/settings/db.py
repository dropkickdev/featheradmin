import os
from dotenv import load_dotenv

from app.settings import settings as s



load_dotenv(override=True)

DATABASE_URL = os.getenv('DATABASE_URL')
DATABASE_MODELS = [
    'aerich.models',
    # 'app.auth.models.user',
    # 'app.auth.models.rbac',
    # 'app.auth.models.core',
    # *get_models_paths()
]
DATABASE = {
    'connections': {
        'default': DATABASE_URL,
    },
    'apps': {
        'models': {
            'models': DATABASE_MODELS,
            "default_connection": "default",
        },
    },
    'timezone': s.TIMEZONE
}