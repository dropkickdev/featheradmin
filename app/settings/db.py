import os
from dotenv import load_dotenv

from app.settings import settings as s



load_dotenv(override=True)

# This should be an exact duplicate of what is in settings for tortoise/aerich to read.
# Using s.DATABASE won't work. You need the actual config dict. Update as needed.
DATABASE_URL = os.getenv('DATABASE_URL')
DATABASE_MODELS = [
    'aerich.models',
    'app.auth.models.user',
    'app.auth.models.rbac',
    'app.auth.models.core',
    # 'authcontrol.models'
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