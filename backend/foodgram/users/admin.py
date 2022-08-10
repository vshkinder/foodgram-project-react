from django.contrib import admin
from import_export.admin import ImportExportModelAdmin, ImportMixin
from .models import CustomUser
from recipes.models import Ingredient, Recipe, Tag, CountOfIngredient


class UsersAdmin(admin.ModelAdmin):
    list_display = ('username', 'password', 'first_name', 'last_name', 'email')
    list_filter = ('username', 'email')
    search_fields = ('username', 'email')
    empty_value_display = "-пусто-"


class FollowsAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    list_filter = ('user', 'author')
    search_fields = ('user', 'author')
    empty_value_display = "-пусто-"


class RecipesAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'count_recipes_favorite')
    list_filter = ('name', 'author', 'tags')
    search_fields = ('name', 'author', 'tags')
    empty_value_display = "-пусто-"
    readonly_fields = ['count_recipes_favorite']

    def count_recipes_favorite(self, obj):
        return obj.recipes_favorite.count()

    count_recipes_favorite.short_description = 'Популярность'


class TagsAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')
    list_filter = ('name',)
    search_fields = ('name',)


class IngredientsAdmin(ImportMixin, admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


admin.site.register(CustomUser, UsersAdmin)
admin.site.register(CountOfIngredient)
admin.site.register(Recipe, RecipesAdmin)
admin.site.register(Tag, TagsAdmin)
admin.site.register(Ingredient, IngredientsAdmin)
