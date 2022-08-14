import traceback

from django.db import IntegrityError
from django.db.models import F
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from rest_framework.fields import SerializerMethodField

from users.models import CustomUser
from users.serializers import UserSerializer

from .models import (CountOfIngredient, Ingredient, Recipe, Shoplist,
                     Tag, RecipesFavorite, TagsRecipe)
from .utils import check_value_validate


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name', 'last_name',)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class CountOfIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient.id'
    )
    name = serializers.CharField(
        read_only=True,
        source='ingredient.name'
    )
    measurement_unit = serializers.CharField(
        read_only=True,
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = CountOfIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class TagSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        required=True,
    )
    slug = serializers.SlugField()

    class Meta:
        model = Tag
        fields = '__all__'
        lookup_field = 'slug'


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.CharField(
        read_only=True, source='recipe.id',
    )
    cooking_time = serializers.CharField(
        read_only=True, source='recipe.cooking_time',
    )
    image = serializers.CharField(
        read_only=True, source='recipe.image',
    )
    name = serializers.CharField(
        read_only=True, source='recipe.name',
    )

    def validate(self, data):
        recipe = data['recipe']
        user = data['user']
        if user == recipe.author:
            raise serializers.ValidationError('Вы автор!')
        if CountOfIngredient.objects.filter(recipe=recipe, user=user).exists():
            raise serializers.ValidationError('Вы уже подписаны!')
        return data

    def create(self, validated_data):
        recipes_favorite = CountOfIngredient.objects.create(**validated_data)
        recipes_favorite.save()
        return recipes_favorite

    class Meta:
        model = RecipesFavorite
        fields = ('id', 'cooking_time', 'name', 'image')


class ShopListSerializer(serializers.ModelSerializer):
    id = serializers.CharField(
        read_only=True,
        source='recipe.id',
    )
    cooking_time = serializers.CharField(
        read_only=True,
        source='recipe.cooking_time',
    )
    image = serializers.CharField(
        read_only=True,
        source='recipe.image',
    )
    name = serializers.CharField(
        read_only=True,
        source='recipe.name',
    )

    class Meta:
        model = Shoplist
        fields = ('id', 'cooking_time', 'name', 'image')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField(
        max_length=None,
        use_url=True,
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = (
            'is_favorite',
            'is_in_shopping_cart',
        )

    def get_status_func(self, data):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        try:
            user = self.context.get('request').user
        except:
            user = self.context.get('user')
        callname_function = format(traceback.extract_stack()[-2][2])
        if callname_function == 'get_is_favorited':
            init_queryset = RecipesFavorite.objects.filter(recipe=data.id, user=user)
        elif callname_function == 'get_is_in_shopping_cart':
            init_queryset = Shoplist.objects.filter(recipe=data, user=user)
        if init_queryset.exists():
            return True
        return False

    def get_is_favorited(self, data):
        return self.get_status_func(data)

    def get_is_in_shopping_cart(self, data):
        return self.get_status_func(data)

    #def validate(self, data):
    #    name = str(self.initial_data.get('name')).strip()
    #    tags = self.initial_data.get('tags')
    #    ingredients = self.initial_data.get('ingredients')
    #    values_as_list = (tags, ingredients)
#
    #    for value in values_as_list:
    #        if not isinstance(value, list):
    #            raise ValidationError(
    #                f'"{value}" должен быть в формате "[]"'
    #            )
#
    #    for tag in tags:
    #        check_value_validate(tag, Tag)
#
    #    valid_ingredients = []
    #    for ing in ingredients:
    #        ing_id = ing.get('id')
    #        ingredient = check_value_validate(ing_id, Ingredient)
#
    #        amount = ing.get('amount')
    #        check_value_validate(amount)
#
    #        valid_ingredients.append(
    #            {'ingredient': ingredient, 'amount': amount}
    #        )
#
    #    data['name'] = name.capitalize()
    #    data['tags'] = tags
    #    data['ingredients'] = valid_ingredients
    #    data['author'] = self.context.get('request').user
    #    return data

    def create(self, validated_data):
        context = self.context['request']
        ingredients = validated_data.pop('recipe_ingredients')
        try:
            recipe = Recipe.objects.create(
                **validated_data,
                author=self.context.get('request').user
            )
        except IntegrityError as err:
            pass
        tags_set = context.data['tags']
        for tag in tags_set:
            TagsRecipe.objects.create(
                recipe=recipe,
                tag=Tag.objects.get(id=tag)
            )
        ingredients_set = context.data['ingredients']
        for ingredient in ingredients_set:
            ingredient_model = Ingredient.objects.get(id=ingredient('id'))
            CountOfIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient_model,
                amount=ingredient['amount'],
            )
        return recipe

    def update(self, instance, validated_data):
        context = self.context['request']
        ingredients = validated_data.pop('recipe_ingredients')
        tags_set = context.data['tags']
        recipe = instance
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        instance.tags.set(tags_set)
        CountOfIngredient.objects.filter(recipe=instance).delete()
        ingredients_req = context.data['ingredients']
        for ingredient in ingredients_req:
            ingredient_model = Ingredient.objects.get(id=ingredient['id'])
            CountOfIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient_model,
                amount=ingredient['amount'],
            )
        return instance

    def to_representation(self, instance):
        response = super(RecipeSerializer, self).to_representation(instance)
        if instance.image:
            response['image'] = instance.image.url
        return response
