from django.contrib.auth.backends import ModelBackend
from .models import User


class EmailAuth(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = User
        try:
            user = user.objects.get(email=username)
        except user.DoesNotExist:
            return None
        if user.check_password(password):
            return user

        return None
