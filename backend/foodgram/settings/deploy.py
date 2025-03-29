from foodgram.settings.base import *
from dotenv import load_dotenv
import os

load_dotenv()

if os.environ.get('DJANGO_DEBUG'):
    DEBUG = True
    # When not specified, ALLOW_HOSTS defaults to:
    # ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']
else:
    DEBUG = False
    ALLOWED_HOSTS = ["*"]

load_dotenv()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_USER_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_DB_PORT"),
    }
}
