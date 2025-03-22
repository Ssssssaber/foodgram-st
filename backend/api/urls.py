from rest_framework.routers import SimpleRouter

from django.urls import include, path

from .views import IngredientViewSet, RecipeViewSet, UserViewSet

appname = 'api'

router = SimpleRouter()
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
]
