from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (
    Ingredient,
    IngredientAndRecipe,
    Recipe
)


User = get_user_model()


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")
        read_only_fields = fields


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAndRecipe
        fields = ("id", "name", "measurement_unit",)


class AuthorSerializer(UserSerializer):
    avatar = Base64ImageField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "avatar",
            "is_subscribed"
        )

    def get_is_subscribed(self, target_user):
        user = self.context.get("request").user

        return user.is_authenticated and user.subscribers.filter(
            target=target_user.id
        ).exists()


class CreateAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ("avatar",)


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )
        read_only_fields = fields


class RecipeSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    ingredients = IngredientRecipeSerializer(
        many=True,
        source="recipe_ingredients"
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        read_only_fields = fields

    def get_is_favorited(self, recipe):
        request = self.context.get("request")
        user = request.user

        return (user.is_authenticated
                and user.favorites.filter(recipe=recipe).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        user = request.user

        return (user.is_authenticated
                and request.user.carts.filter(recipe=obj).exists())


class SubscriberSerializer(AuthorSerializer):
    recipes = serializers.SerializerMethodField(method_name="get_recipes")
    recipes_count = serializers.IntegerField(source="recipes.count")
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id", "email", "username", "first_name", "last_name",
            "recipes", "recipes_count", "avatar", "is_subscribed"
        )

    def get_recipes(self, obj):
        queryset = obj.recipes.all()
        request = self.context.get("request")
        recipes_limit = request.GET.get("recipes_limit")
        if recipes_limit:
            queryset = queryset[:int(recipes_limit)]

        return ShortRecipeSerializer(
            queryset, context={"request": request}, many=True
        ).data

    def get_is_subscribed(self, target_user):
        user = self.context.get("request").user

        return user.is_authenticated and user.subscribers.filter(
            target=target_user.id
        ).exists()


class CreateIngredientSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient')
    amount = serializers.IntegerField(
        min_value=1
    )

    class Meta:
        model = Ingredient
        fields = ("id", "amount")


class CreateRecipeSerializer(serializers.ModelSerializer):
    ingredients = CreateIngredientSerializer(many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        min_value=1
    )

    class Meta:
        model = Recipe
        fields = (
            "ingredients",
            "name",
            "image",
            "name",
            "text",
            "cooking_time",
        )

    def validate(self, data):
        ingredients = data.get("ingredients")

        if not ingredients:
            raise serializers.ValidationError(
                {"ingredients": "Обязательное поле"}
            )

        ingredients_ids = [
            ingredient["ingredient"].id
            for ingredient in ingredients
        ]
        if len(ingredients_ids) != len(set(ingredients_ids)):
            raise serializers.ValidationError(
                {"ingredients": "Ингредиенты не должны повторяться"}
            )

        return data

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError(
                {"image": "Обязательное поле"}
            )

        return value

    def create(self, validated_data):
        ingredients = validated_data.pop("ingredients")
        recipe = super().create(validated_data)
        self.create_ingredients(ingredients, recipe)

        return recipe

    def update(self, instance, validated_data):
        IngredientAndRecipe.objects.filter(recipe=instance).delete()
        self.create_ingredients(validated_data.pop("ingredients"), instance)

        return super().update(instance, validated_data)

    def create_ingredients(self, ingredients, recipe):
        IngredientAndRecipe.objects.bulk_create(
            IngredientAndRecipe(
                ingredient_id=ingredient["ingredient"].id,
                recipe=recipe,
                amount=ingredient["amount"]
            )
            for ingredient in ingredients
        )

    def to_representation(self, instance):
        return RecipeSerializer(
            instance,
            context=self.context
        ).data
