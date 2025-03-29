from foodgram.settings.base import *


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        "NAME": "foodgram",
        "USER": "foodgram_admin",
        "PASSWORD": "kekeispassword",
        "HOST": "localhost",
        "PORT": 5432,
    }
}
