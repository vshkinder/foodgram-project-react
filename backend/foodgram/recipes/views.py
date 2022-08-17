from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from .filters import TagsFilter
from .models import Ingredient, Recipe, Shoplist, Tag, RecipesFavorite, CountOfIngredient
from .permissions import AuthorOrReadOnly
from .serializers import (IngredientSerializer,
                          RecipeSerializer, SimpleRecipeSerializer, TagSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TagsFilter
    permission_classes = [AuthorOrReadOnly]

    def get_queryset(self):
        queryset = Recipe.objects.all()
        is_favorited = self.request.query_params.get('is_favorited')
        is_in_shopping_cart = self.request.query_params.get('is_in_shopping_cart')
        if is_favorited:
            queryset = queryset.filter(recipes_favorite__user=self.request.user)
        if is_in_shopping_cart:
            queryset = queryset.filter(shopping_cart__user=self.request.user)
        return queryset


    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            return self.add_obj(RecipesFavorite, request.user, pk)
        elif request.method == 'DELETE':
            return self.delete_obj(RecipesFavorite, request.user, pk)
        return None

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.add_obj(Shoplist, request.user, pk)
        elif request.method == 'DELETE':
            return self.delete_obj(Shoplist, request.user, pk)
        return None

    @action(methods=('GET',), detail=False)
    def download_shopping_cart(self, request):
        shop_list = {}
        ingredients = CountOfIngredient.objects.filter(
            recipe__shopping_cart__user=request.user).values_list(
            'ingredients__name', 'ingredients__measurement_unit',
            'amount'
        )
        for item in ingredients:
            name = item[0]
            if name not in shop_list:
                shop_list[name] = {
                    'measurement_unit': item[1],
                    'amount': item[2]
                }
            else:
                shop_list[name]['amount'] += item[2]
#        pdfmetrics.registerFont(
#            TTFont('FUTURAM', 'FUTURAM.ttf', 'UTF-8'))
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = ('attachment; '
                                           'filename="shopping_list.pdf"')
        page = canvas.Canvas(response)
#        page.setFont('FUTURAM', size=24)
        page.drawString(200, 800, 'Список ингредиентов')
#       page.setFont('FUTURAM', size=16)
        height = 750
        for i, (name, data) in enumerate(shop_list.items(), 1):
            page.drawString(75, height, (f'<{i}> {name} - {data["amount"]}, '
                                         f'{data["measurement_unit"]}'))
            height -= 25
        page.showPage()
        page.save()
        return response

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
