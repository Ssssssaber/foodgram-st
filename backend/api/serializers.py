from rest_framework import serializers  # , validators
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
# from rest_framework.relations import SlugRelatedField
from recipes.models import (
    Ingredient,
    Recipe,
    IngredientAndRecipe,
    FavoriteUserRecipes,
    UserCart
)
from custom_user.models import Subscription


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Ingredient
        read_only_fields = ("id", "name", "measurement_unit")


class IngredientAndRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measure'
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientAndRecipe
        fields = ("id", "name", "measure", "amount")


class IsSubscribedSerializer(serializers.Serializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user

        if (not user.is_authenticated):
            return False

        return user.subscriptions.filter(target=obj.id).exists()


class AvatarSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=True)

    class Meta:
        model = get_user_model()
        fields = ("avatar",)

    def validate(self, attrs):
        if 'avatar' not in attrs:
            raise serializers.ValidationError(
                {"avatar": "Обязательное поле"}
            )
        return super().validate(attrs)

    def validate_avatar(self, value):
        if not value:
            raise serializers.ValidationError(
                {"avatar": "Обязательное поле"}
            )
        return value


class AuthorSerializer(UserSerializer, IsSubscribedSerializer):
    avatar = serializers.ImageField()

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


class RecipeSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    ingredients = IngredientAndRecipeSerializer(
        many=True,
        source="recipe_ingredients"
    )
    is_favorite = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = (
            "id",
            "author",
            "ingredients",
            "is_favorite",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        model = Recipe


class CreateUser(UserCreateSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
        )


class MinimizedRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class SubscriberSerializer(AuthorSerializer, IsSubscribedSerializer):
    recipes = serializers.SerializerMethodField(method_name="get_recipes")
    recipes_count = serializers.IntegerField(source="recipes.count")

    class Meta:
        model = get_user_model
        fields = (
            "id", "email", "username", "first_name", "last_name",
            "recipes", "recipes_count", "avatar", "is_subscribed"
        )

    def get_recipes(self, obj):
        queryset = obj.recipes.all()
        request = self.context.get("request")
        recipes_limit = request.query_params.get("recipes_limit")
        if recipes_limit and recipes_limit.isdigit():
            queryset = queryset[:int(recipes_limit)]

        return MinimizedRecipeSerializer(
            queryset, context={"request": request}, many=True
        ).data


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = (
            "subscribing_user", "target"
        )


class RecipeCollectionSerializer(serializers.ModelSerializer):

    class Meta:
        abstract = True
        fields = ("user", "recipe")

    def to_representation(self, instance):
        serializer = MinimizedRecipeSerializer(
            instance.recipe,
            context=self.context
        )
        return serializer.data

    def validate(self, attrs):
        queryset = self.Meta.model.objects
        user = attrs["user"]
        recipe = attrs["recipe"]

        if queryset.filter(
            recipe=recipe,
            user=user
        ).exists():
            raise serializers.ValidationError(
                "Запись уже существует"
            )

        return super().validate(attrs)


class FavoriteSerializer(RecipeCollectionSerializer):
    class Meta(RecipeCollectionSerializer.Meta):
        model = FavoriteUserRecipes


class CartSerializer(RecipeCollectionSerializer):
    class Meta(RecipeCollectionSerializer.Meta):
        model = UserCart


class CreateIngredientSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        fields = ("id", "amount")

    def validate_id(self, value):
        ingredient = Ingredient.objects.filter(pk=value)

        if not ingredient.exists():
            raise serializers.ValidationError(
                {"id": "Недействительный идентификатор"}
            )

        return value

    def validate_amount(self, value):
        if not value >= 0:
            raise serializers.ValidationError(
                {"amount": "Недопустимое значение"}
            )

        return value


class CreateRecipeSerializer(serializers.ModelSerializer):
    ingredients = CreateIngredientSerializer(many=True)
    image = serializers.ImageField()

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
            ingredient["id"]
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
        user = self.context.get("request").user
        recipe = Recipe.objects.create(**validated_data, author=user)
        self.create_ingredients(ingredients, recipe)

        return recipe

    def update(self, instance, validated_data):
        IngredientAndRecipe.objects.filter(recipe=instance).delete()
        self.create_ingredients(validated_data.pop("ingredients"), instance)

        return super().update(instance, validated_data)

    def create_ingredients(self, ingredients, recipe):
        IngredientAndRecipe.objects.bulk_create(
            IngredientAndRecipe(
                ingredient_id=ingredient["id"],
                recipe=recipe,
                amount=ingredient["amount"]
            )
            for ingredient in ingredients
        )

    def to_representation(self, instance):
        serializer = RecipeSerializer(
            instance,
            context={"request": self.context.get("request")}
        )
        return serializer.data
