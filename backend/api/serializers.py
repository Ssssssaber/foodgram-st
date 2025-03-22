from rest_framework import serializers  # , validators
from django.contrib.auth import get_user_model
# from rest_framework.relations import SlugRelatedField


from recipes.models import Ingredient, Recipe


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Ingredient


class RecipeSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Recipe


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = get_user_model()
