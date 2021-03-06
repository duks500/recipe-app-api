from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient, Recipe

from recipe import serializers


# The goal of this class is to make the code less and more easy
# If the class have shared attributes, it will make is easier
class BaseRecipeAttrViewSet(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin):
    """Base viewset for user owned recipe attributes"""
    # Pre-define class variables in the viewsets class
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return objects for the current authenticateduser only"""
        assigned_only = bool(
            # Convert parm to int and bool because query dont know types
            # If there is no value, assigned it to 0
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        # If the assigned_only is true, we apply filter that makes the recipe
        # To be equal to false and return only assigned recipes
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)

        return queryset.filter(
            user=self.request.user
        ).order_by('-name').distinct()

    def perform_create(self, serializer):
        """Create a new object"""
        # Can be a new Tag or a new Ingredient
        # Save to serializer with the user as the authenticated user
        serializer.save(user=self.request.user)


# Mixin allowed us to costumise the viewset so we could choose whatever we want
class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the database"""
    # Pre-define class variables in the viewsets class
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingrident in the database"""
    # Pre-define class variables in the viewsets class
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Manage recipes in the database"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()

    # A function that intented to be private
    def _params_to_ints(self, qs):
        """Convert a list of strings IDs to a list of integers"""
        # Split the string by the ',' so for example list of '1,2,3' will be->
        # ['1','2','3']
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrieve the recipes for the authenticated user"""
        # check if tags has been provided
        tags = self.request.query_params.get('tags')
        # check if ingredients has been provided
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset

        if tags:
            tag_ids = self._params_to_ints(tags)
            # a way to filter using atags__
            # first the tags will return all the id and then will return->
            # all the ids within the tags
            queryset = queryset.filter(tags__id__in=tag_ids)

        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)

        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save(user=self.request.user)

    # Upload image to recipes that already exists
    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to a recipe"""
        recipe = self.get_object()
        serializer = self.get_serializer(
            recipe,
            data=request.data
        )

        # Return if the data is vaild
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        # Return if the data is not vaild
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
