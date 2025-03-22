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
