import django_filters as filters
from django_filters.widgets import BooleanWidget

from recipes.models import Recipe
from users.models import CustomUser


class TagsFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = ('tags',)
