from foodgram.settings.base import *


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        "NAME": "foodgram",
        "USER": "postgres",
        "PASSWORD": "keke",
        "HOST": "localhost",
        "PORT": 5432,
        'DISABLE_SERVER_SIDE_CURSORS': True,
    }
}
