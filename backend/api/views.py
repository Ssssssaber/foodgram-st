from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Sum
import json
from rest_framework import (
    viewsets,
    permissions,
    status,
    response,
    filters
)
from rest_framework.decorators import action
from recipes.models import Ingredient, Recipe, UserCart
from .serializers import (
    IngredientSerializer,
    SubscriptionSerializer,
    SubscriberSerializer,
    RecipeSerializer,
    UserSerializer,
    FavoriteSerializer,
    AvatarSerializer,
    CartSerializer
)
from .permissions import ApiPermission


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ("^name",)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (ApiPermission,)
    serializer_class = RecipeSerializer

    @action(
        detail=True,
        methods=("post", "delete"),
        url_path="favorite",
        url_name="favorite",
        permission_classes=(permissions.IsAuthenticated,)
    )
    def favorite(self, request, pk):
        get_object_or_404(
            Recipe,
            pk=pk
        )

        if request.method == "POST":
            return self.create_recipe_collection(
                request, pk, FavoriteSerializer
            )
        return self.delete_recipe_collection(
            request, pk, FavoriteSerializer.Meta.model.objects
        )

    @action(
        detail=True,
        methods=("post", "delete"),
        url_path="shopping_cart",
        url_name="shopping_cart",
        permission_classes=(permissions.IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        get_object_or_404(
            Recipe,
            pk=pk
        )

        if request.method == "POST":
            return self.create_recipe_collection(
                request, pk, CartSerializer
            )
        return self.delete_recipe_collection(
            request, pk, CartSerializer.Meta.model.objects
        )

    def create_recipe_collection(self, request, pk, serializer_class):
        serializer = serializer_class(
            data={
                "user": request.user.id,
                "recipe": pk,
            }
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return response.Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def delete_recipe_collection(self, request, pk, queryset):
        recipe = queryset.filter(user=request.user, recipe_id=pk)
        if recipe.exists():
            recipe.delete()
            return response.Response(status=status.HTTP_204_NO_CONTENT)
        return response.Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=("get",),
        url_path="download_shopping_cart",
        url_name="download_shopping_cart",
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients = UserCart.objects.filter(
            user=request.user
        ).values(
            "recipe__ingredients_in_recipe__ingredient__name",
            "recipe__ingredients_in_recipe__ingredient__measurement_unit"
        ).annotate(
            total=Sum('recipe__ingredients_in_recipe__amount')
        )

        return self.ingredients_to_json(ingredients)

    def ingredients_to_json(self, ingredients):
        shopping_list = []
        for ingredient in ingredients:
            list_item = {}
            list_item['name'] = ingredient[
                "recipe__ingredients_in_recipe__ingredient__name"
            ]
            list_item['unit'] = ingredient[
                "recipe__ingredients_in_recipe__ingredient__measurement_unit"
            ]
            list_item['total'] = ingredient["total"]
            shopping_list.append(list_item)

        file = json.dumps(shopping_list)

        return response.FileResponse(
            file,
            as_attachment=True,
            filename="Список покупок.json",
            content_type="text/json"
        )

    @action(
        detail=True,
        methods=("get",),
        url_path="get-link",
        url_name="get-link",
    )
    def get_short_link(self, request, pk):
        instance = self.get_object()
        url = f"{request.get_host()}/s/{instance.pk}"

        return response.Response(
            data={
                "short-link": url
            }
        )


class UserViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()
    permission_classes = (ApiPermission,)
    serializer_class = UserSerializer

    def get_permissions(self):
        """Переопределяем разрешения для разных эндпоинтов."""
        if self.action in ["me", "avatar"]:
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    @action(
        detail=True,
        methods=("put", "delete"),
        url_path="avatar",
        url_name="avatar",
        permission_classes=(permissions.IsAuthenticated,)
    )
    def avatar(self, request, id):
        if request.method == "PUT":
            return self.create_avatar(request)
        return self.delete_avatar(request)

    def create_avatar(self, request):
        serializer = AvatarSerializer(
            request.user,
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return response.Response(
            serializer.data
        )

    def delete_avatar(self, request):
        user = request.user
        if user.avatar:
            user.avatar.delete()
            user.avatar = None
            user.save()

        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=("get",),
        url_path="subscriptions",
        url_name="subscriptions",
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscriptions(self, request):
        targets = request.user.subscriptions.values("target")
        queryset = self.get_queryset().filter(
            pk__in=targets
        )
        pages = self.paginate_queryset(queryset)
        serializer = SubscriberSerializer(
            pages, many=True, context={"request": request}
        )

        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=("post", "delete"),
        url_path="subscribe",
        url_name="subscribe",
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscribe(self, request, id):
        get_object_or_404(
            get_user_model(),
            pk=id
        )
        if request.method == "POST":
            return self.create_subscription(request, id)
        return self.delete_subscription(request, id)

    def create_subscription(self, request, pk):
        if request.user.pk == int(pk):
            return response.Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = SubscriptionSerializer(
            data={
                "subscribing_user": request.user.pk,
                "target": pk,
            },
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response_serializer = SubscriberSerializer(
            self.get_queryset().get(pk=pk),
            context={"request": request}
        )

        return response.Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )

    def delete_subscription(self, request, pk):
        queryset = SubscriptionSerializer.Meta.model.objects
        subscription = queryset.filter(
            subscribing_user=request.user, target_id=pk
        )
        if subscription.exists():
            subscription.delete()
            return response.Response(status=status.HTTP_204_NO_CONTENT)
        return response.Response(status=status.HTTP_400_BAD_REQUEST)
