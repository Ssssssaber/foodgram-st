from django.contrib import admin
from .models import Ingridient, Recipe

# Register your models here.
admin.site.register(Ingridient)
admin.site.register(Recipe)
