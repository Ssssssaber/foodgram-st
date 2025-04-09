from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404, reverse
from django_filters import rest_framework
from djoser import views
from datetime import datetime
from rest_framework import (
    decorators,
    filters,
    permissions,
    response,
    status,
    viewsets
)

from api.permissions import IsAuthorOrReadOnlyPermission
from api.serializers import (
    CreateAvatarSerializer,
    CreateRecipeSerializer,
    IngredientSerializer,
    RecipeSerializer,
    ShortRecipeSerializer,
    SubscriberSerializer,
)
from recipes.models import (
    Ingredient,
    Recipe,
    Cart,
    FavoriteUserRecipes,
    Subscription
)


class IngredientViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    search_fields = ("^name",)
    filter_backends = (filters.SearchFilter,)
    permission_classes = (permissions.AllowAny,)
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.query_params.get("name", None)
        if name:
            queryset = queryset.filter(name__istartswith=name)
        return queryset


class UserViewSet(views.UserViewSet):
    queryset = get_user_model().objects.all()
    permission_classes = (IsAuthorOrReadOnlyPermission, )

    @decorators.action(
        detail=False,
        methods=('get',),
        url_path='me',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def me(self, request):
        return super().me(request)

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
                        pk__in=request.user.subscribers.values("target")
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
        author = get_object_or_404(
            get_user_model(),
            pk=id
        )

        if request.method == "POST":
            if request.user == author:
                return response.Response(
                    {"Fail": "Попытка подписаться на самого себя"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            subscription, created = Subscription.objects.get_or_create(
                subscribing_user=request.user,
                target=author
            )
            if created:
                return response.Response(
                    SubscriberSerializer(
                        author,
                        context={"request": request}
                    ).data,
                    status=status.HTTP_201_CREATED
                )
            return response.Response(
                {"Fail": "Попытка подписаться на самого себя"},
                status=status.HTTP_409_CONFLICT
            )

        get_object_or_404(
            Subscription,
            subscribing_user=request.user,
            target=author
        ).delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnlyPermission, )
    filter_backends = (rest_framework.DjangoFilterBackend,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ("create", "partial_update"):
            return CreateRecipeSerializer
        return RecipeSerializer

    def manage_recipe_collection(self, request, pk, model, error_message):
        recipe = get_object_or_404(
            Recipe,
            pk=pk
        )

        if request.method == "POST":
            favorite, created = model.objects.get_or_create(
                user=request.user,
                recipe=recipe,
            )

            if created:
                return response.Response(
                    ShortRecipeSerializer(recipe).data,
                    status=status.HTTP_201_CREATED
                )
            return response.Response(
                {"Fail": error_message},
                status=status.HTTP_409_CONFLICT
            )

        get_object_or_404(
            model,
            user=request.user,
            recipe_id=pk
        ).delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(
        detail=True,
        methods=("post", "delete"),
        url_path="favorite",
        url_name="favorite",
        permission_classes=(permissions.IsAuthenticated,)
    )
    def favorite(self, request, pk):
        return self.manage_recipe_collection(
            request,
            pk,
            FavoriteUserRecipes,
            "Рецепт уже в избранном"
        )

    @decorators.action(
        detail=True,
        methods=("post", "delete"),
        url_path="shopping_cart",
        url_name="shopping_cart",
        permission_classes=(permissions.IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        return self.manage_recipe_collection(
            request,
            pk,
            Cart,
            "Рецепт уже в корзине"
        )

    @decorators.action(
        detail=False,
        methods=("get",),
        url_path="download_shopping_cart",
        url_name="download_shopping_cart",
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients = Cart.objects.filter(
            user=request.user
        ).values(
            "recipe__recipe_ingredients__ingredient__name",
            "recipe__recipe_ingredients__ingredient__measurement_unit"
        ).annotate(
            total=Sum("recipe__recipe_ingredients__amount")
        ).order_by(
            "recipe__recipe_ingredients__ingredient__name"
        )

        recipes = request.user.carts.all()

        file = "\n".join([
            "Список покупок {username} ({date}):".format(
                username=request.user.username,
                date=datetime.now()
            ),
            "Продукты:",
            *(
                "{i}. {name} {amount} {measurement_unit}".format(
                    i=i,
                    name=ingredient[
                        "recipe__recipe"
                        "_ingredients__ingredient__name"
                    ].capitalize(),
                    amount=ingredient["total"],
                    measurement_unit=ingredient[
                        "recipe__recipe_ingredients"
                        "__ingredient__measurement_unit"
                    ]
                ) for i, ingredient in enumerate(ingredients, start=1)
            ),
            "Рецепты:",
            *(
                "{i}. {name} от {author}".format(
                    i=i,
                    name=recipe,
                    author=recipe.recipe.author
                )
                for i, recipe in enumerate(recipes, start=1)
            ),
        ])

        return FileResponse(
            file,
            as_attachment=True,
            filename="shopping-list.txt",
            content_type="text/plain",
        )

    @decorators.action(
        detail=True,
        methods=("get",),
        url_path="get-link",
        url_name="get-link",
    )
    def return_short_link(self, request, pk):
        get_object_or_404(Recipe, pk=pk)
        return response.Response({
            "short-link": request.build_absolute_uri(
                reverse("recipes:get_recipe_link", args=(pk,))
            )
        })
