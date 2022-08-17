import django_filters as filters
from django_filters.widgets import BooleanWidget

from .models import Recipe, Tag
from users.models import CustomUser


class RecipeFilter(filters.FilterSet):
#    author = filters.ModelChoiceFilter(
#        queryset=CustomUser.objects.all())
#    is_in_shopping_cart = filters.BooleanFilter(
#        widget=BooleanWidget(),
#        label='В корзине.')
#    is_favorited = filters.BooleanFilter(
#        widget=BooleanWidget(),
#        label='В избранных.')
#    tags = filters.AllValuesMultipleFilter(
#        field_name='tags__slug',
#        label='Ссылка')
#
#    class Meta:
#        model = Recipe
#        fields = ['author', 'tags']

    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
#    author = filters.ModelChoiceFilter(queryset=CustomUser.objects.all())
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        return queryset.filter(is_favorited=self.request.user)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(is_in_shopping_cart=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')
