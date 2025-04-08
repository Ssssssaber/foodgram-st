
import json
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters import rest_framework
from djoser import views
from rest_framework import (
    decorators,
    filters,
    permissions,
    response,
    status,
    viewsets
)

from api.permissions import IsMethodSafePermission
from api.serializers import (
    CartSerializer,
    CreateAvatarSerializer,
    CreateRecipeSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    RecipeSerializer,
    SubscriberSerializer,
    SubscriptionSerializer
)
from recipes.models import Ingredient, Recipe, UserCart, FavoriteUserRecipes
from custom_user.models import Subscription

get_user_model_cache = []
get_recipe_cache = []


class IngredientViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    search_fields = ("^name",)
    filter_backends = (filters.SearchFilter,)
    permission_classes = (permissions.AllowAny,)
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.query_params.get('name', None)
        if name:
            queryset = queryset.filter(name__istartswith=name)
        return queryset


class UserViewSet(views.UserViewSet):
    queryset = get_user_model().objects.all()
    permission_classes = (IsMethodSafePermission,)

    def has_permission(self, request, view):
        if view.action == "me":
            return request.user.is_authenticated
        else:
            return super().has_permission(request, view)

    @decorators.action(
        detail=True,
        methods=("put", "delete"),
        url_path="avatar",
        url_name="avatar",
        permission_classes=(permissions.IsAuthenticated,)
    )
    def avatar(self, request, id):
        if request.method == "PUT":
            serializer = CreateAvatarSerializer(
                request.user,
                data=request.data,
                context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return response.Response(
                serializer.data
            )
        else:
            user = request.user
            if user.avatar:
                user.avatar.delete()
                user.avatar = None
                user.save()

            return response.Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(
        detail=False,
        methods=("get",),
        url_path="subscriptions",
        url_name="subscriptions",
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscriptions(self, request):
        return self.get_paginated_response(
            SubscriberSerializer(
                self.paginate_queryset(
                    self.get_queryset().filter(
                        pk__in=request.user.subscriptions.values("target")
                    )
                ),
                many=True,
                context={"request": request}
            ).data
        )

    @decorators.action(
        detail=True,
        methods=("post", "delete"),
        url_path="subscribe",
        url_name="subscribe",
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscribe(self, request, id):
        if id not in get_user_model_cache:
            get_object_or_404(
                get_user_model(),
                pk=id
            )
            get_user_model_cache.append(id)

        if request.method == "POST":
            if request.user.pk == int(id):
                return response.Response(
                    {"Fail": "Попытка подписаться на самого себя"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = SubscriptionSerializer(
                data={
                    "subscribing_user": request.user.pk,
                    "target": id,
                },
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return response.Response(
                SubscriberSerializer(
                    self.get_queryset().get(pk=id),
                    context={"request": request}
                ).data,
                status=status.HTTP_201_CREATED
            )

        get_object_or_404(Subscription, subscribing_user=request.user).delete()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsMethodSafePermission,)
    filter_backends = (rest_framework.DjangoFilterBackend,)

    def get_serializer_class(self):
        if self.action in ("create", "partial_update"):
            return CreateRecipeSerializer
        else:
            return RecipeSerializer

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

    @decorators.action(
        detail=True,
        methods=("post", "delete"),
        url_path="favorite",
        url_name="favorite",
        permission_classes=(permissions.IsAuthenticated,)
    )
    def favorite(self, request, pk):
        if pk not in get_recipe_cache:
            get_object_or_404(
                Recipe,
                pk=pk
            )
            get_recipe_cache.append(pk)

        if request.method == "POST":
            return self.create_recipe_collection(
                request, pk, FavoriteSerializer
            )

        get_object_or_404(
            FavoriteUserRecipes,
            user=request.user,
            recipe_id=pk
        ).delete()

    @decorators.action(
        detail=True,
        methods=("post", "delete"),
        url_path="shopping_cart",
        url_name="shopping_cart",
        permission_classes=(permissions.IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        if pk not in get_recipe_cache:
            get_object_or_404(
                Recipe,
                pk=pk
            )
            get_recipe_cache.append(pk)

        if request.method == "POST":
            return self.create_recipe_collection(
                request, pk, CartSerializer
            )
        get_object_or_404(
            UserCart,
            user=request.user,
            recipe_id=pk
        ).delete()

    @decorators.action(
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
            "recipe__recipe_ingredients__ingredient__name",
            "recipe__recipe_ingredients__ingredient__measurement_unit"
        ).annotate(
            total=Sum('recipe__recipe_ingredients__amount')
        )

        shopping_list = []
        for ingredient in ingredients:
            shoppint_item = {}
            shoppint_item['name'] = ingredient[
                "recipe__recipe_ingredients__ingredient__name"
            ]
            shoppint_item['measurement_unit'] = ingredient[
                "recipe__recipe_ingredients__ingredient__measurement_unit"
            ]
            shoppint_item['total'] = ingredient["total"]
            shopping_list.append(shoppint_item)

        response_file = json.dumps(shopping_list)

        return FileResponse(
            response_file,
            as_attachment=True,
            filename="shop-list.json",
            content_type="application/json"
        )

    @decorators.action(
        detail=True,
        methods=("get",),
        url_path="get-link",
        url_name="get-link",
    )
    def return_short_link(self, request, pk):
        instance = self.get_object()
        url = f"{request.get_host()}/s/{instance.pk}"

        return response.Response(
         
            data={"short-link": url}
        )
