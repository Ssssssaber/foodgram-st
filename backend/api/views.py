from django.contrib.auth import get_user_model
# from django.shortcuts import get_object_or_404
from rest_framework import (
    viewsets,
    # decorators,
    # permissions,
    # status,
    # response,
    # filters
)
from recipes.models import Ingredient, Recipe
from .serializers import IngredientSerializer, RecipeSerializer, UserSerializer

from django.core.management import call_command


def backup(filename, app):
    saveDir = open("{}.json".format(filename), 'w')

    # change application_name with your django app which you want to get
    #  backup from it
    call_command('dumpdata', stdout=saveDir, indent=3)
    saveDir.close()


# backup('users_backup', 'custom_user')
backup('recipes_backup', 'recipes')


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    search_fileds = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
