from rest_framework.routers import SimpleRouter

from django.urls import include, path

from .views import IngredientViewset, RecipeViewSet, UserViewSet

app_name = 'api'
router = SimpleRouter()
router.register('ingredients', IngredientViewset, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path("", include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
