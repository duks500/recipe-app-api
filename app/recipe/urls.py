from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recipe import views


# Router alredy register the diffrent URLs to all of the viewsets
# Set up the router
router = DefaultRouter()
# Give the router a name
router.register('tags', views.TagViewSet)
router.register('ingredients', views.IngredientViewSet)
router.register('recipes', views.RecipeViewSet)

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls)),
]
