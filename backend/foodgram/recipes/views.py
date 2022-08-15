from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly, SAFE_METHODS)
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from .filters import RecipeFilter
from .models import Ingredient, Recipe, Shoplist, Tag, RecipesFavorite, CountOfIngredient
from .permissions import IsAuthorOrAdminOrReadOnly, AuthorOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeSerializer, SimpleRecipeSerializer, TagSerializer)
from .utils import get_shopping_list


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = RecipeFilter
    permission_classes = [AuthorOrReadOnly]

    @action(detail=True, methods=['get', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        if request.method == 'GET':
            return self.add_obj(RecipesFavorite, request.user, pk)
        elif request.method == 'DELETE':
            return self.delete_obj(RecipesFavorite, request.user, pk)
        return None

    @action(
        detail=True,
        methods=['GET', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        if request.method == 'GET':
            return self.add_obj(Shoplist, request.user, pk)
        elif request.method == 'DELETE':
            return self.delete_obj(Shoplist, request.user, pk)
        return None

    @action(methods=('GET',), detail=False)
    def download_shopping_cart(self, request):
        try:
            return get_shopping_list(request)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def add_obj(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({
                'errors': 'Рецепт уже добавлен в список'
            }, status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = SimpleRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_obj(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({
            'errors': 'Рецепт уже удален'
        }, status=status.HTTP_400_BAD_REQUEST)


class IngredientsViewSet(viewsets.ModelViewSet):
    pagination_class = None
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class TagsViewSet(viewsets.ModelViewSet):
    pagination_class = None
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
