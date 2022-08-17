import django_filters as filters

from .models import Recipe, Tag
from users.models import CustomUser


class RecipeFilter(filters.FilterSet):
    author = filters.ModelChoiceFilter(
        queryset=CustomUser.objects.all())
    is_in_shopping_cart = filters.BooleanFilter(
        widget=filters.widgets.BooleanWidget(),
        label='В корзине.')
    is_favorited = filters.BooleanFilter(
        widget=filters.widgets.BooleanWidget(),
        label='В избранных.')
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
        label='Ссылка')

    class Meta:
        model = Recipe
        fields = ['author', 'tags']
#    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
#    author = filters.ModelChoiceFilter(queryset=CustomUser.objects.all())
#    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
#    is_in_shopping_cart = filters.BooleanFilter(
#        method='filter_is_in_shopping_cart')
#
#    def filter_is_favorited(self, queryset, name, value):
#        if value and not self.request.user.is_anonymous:
#            return queryset.filter(recipes_favorite__user=self.request.user)
#        return queryset
#
#    def filter_is_in_shopping_cart(self, queryset, name, value):
#        if value and not self.request.user.is_anonymous:
#            return queryset.filter(shopping_cart__user=self.request.user)
#        return queryset
#
#    class Meta:
#        model = Recipe
#        fields = ('tags', 'author')
