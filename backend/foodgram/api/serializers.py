import datetime as dt

from django.db import IntegrityError
from django.db.models import Avg
from rest_framework import exceptions, serializers
from rest_framework_simplejwt.tokens import RefreshToken
from recipes.models import Tag, Ingredient, Recipe, CountOfIngredient, Favorite, Shop_list
from users.models import User

from .validators import validate_username


class UserSerializer(serializers.ModelSerializer):
    def validate_username(self, value):
        return validate_username(value)

    class Meta:
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
        )
        model = User


class UserMeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
        )
        read_only_fields = ('role',)
        model = User


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class RecipeSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )