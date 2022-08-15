#from django.core.exceptions import ValidationError
#import django_filters as filters
#
#from .models import Recipe, Tag, Ingredient
#from users.models import CustomUser
#
#
#class TagsMultipleChoiceField(
#        filters.fields.MultipleChoiceField):
#    def validate(self, value):
#        if self.required and not value:
#            raise ValidationError(
#                self.error_messages['required'],
#                code='required')
#        for val in value:
#            if val in self.choices and not self.valid_value(val):
#                raise ValidationError(
#                    self.error_messages['invalid_choice'],
#                    code='invalid_choice',
#                    params={'value': val},)
#
#
#class TagsFilter(filters.AllValuesMultipleFilter):
#    field_class = TagsMultipleChoiceField
#
#
#class IngredientFilter(filters.FilterSet):
#    name = filters.CharFilter(lookup_expr='istartswith')
#
#    class Meta:
#        model = Ingredient
#        fields = ('name',)
#
#
#class RecipeFilter(filters.FilterSet):
#    author = filters.ModelChoiceFilter(
#        queryset=CustomUser.objects.all())
#    is_in_shopping_cart = filters.BooleanFilter(
#        widget=filters.widgets.BooleanWidget(),
#        label='В корзине.')
#    is_favorited = filters.BooleanFilter(
#        widget=filters.widgets.BooleanWidget(),
#        label='В избранных.')
#    tags = filters.AllValuesMultipleFilter(
#        field_name='tags__slug',
#        label='Ссылка')
#
#    class Meta:
#        model = Recipe
#        fields = ['is_favorited', 'is_in_shopping_cart', 'author', 'tags']


#class RecipeFilter(filters.FilterSet):
#    tags = filters.filters.AllValuesMultipleFilter(
#        queryset=Tag.objects.all(),
#        field_name='tags__slug',
#        to_field_name='slug',
#    )
#    author = filters.CharFilter(lookup_expr='exact')
#    is_in_shopping_cart = filters.BooleanFilter(
#        field_name='is_in_shopping_cart', method='filter'
#    )
#    is_favorited = filters.BooleanFilter(
#        field_name='is_favorited', method='filter'
#    )
#
#    def filter(self, queryset, name, value):
#        if name == 'is_in_shopping_cart' and value:
#            queryset = queryset.filter(
#                shopping_cart__user=self.request.user
#            )
#        if name == 'is_favorited' and value:
#            queryset = queryset.filter(
#                recipes_favorite__user=self.request.user
#            )
#        return queryset
#
#    class Meta:
#        model = Recipe
#        fields = ['author', 'tags', 'is_in_shopping_cart', 'is_favorited']
