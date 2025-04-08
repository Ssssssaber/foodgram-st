from django.urls import path

from .views import get_recipe_link

app_name = 'recipes'

urlpatterns = [
    path('s/<int:recipe_id>/', get_recipe_link, name='get_recipe_link'),
]
