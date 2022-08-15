import traceback

from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from users.models import CustomUser

from .models import (CountOfIngredient, Ingredient, Recipe, Shoplist,
                     Tag, RecipesFavorite)


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
        favorite = CountOfIngredient.objects.create(**validated_data)
        favorite.save()
        return favorite

    class Meta:
        model = RecipesFavorite
        fields = ('id', 'cooking_time', 'name', 'image')


class RecipeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        required=True,
    )
    tags = TagSerializer(many=True, read_only=True)
    author = AuthorSerializer(read_only=True)
    ingredients = CountOfIngredientSerializer(
        many=True, source='recipe_ingredients'
    )
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField(
        max_length=None,
        use_url=True,
    )
    text = serializers.CharField()
    cooking_time = serializers.IntegerField(max_value=32767, min_value=1)

    class Meta:
        model = Recipe
        exclude = ('pub_date',)
        read_only_fields = (
            'is_favorite',
            'is_in_shopping_cart',
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Recipe.objects.filter(recipes_favorite__user=user, id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Recipe.objects.filter(shopping_cart__user=user, id=obj.id).exists()

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': 'Нужен хоть один ингридиент для рецепта'})
        ingredient_list = []
        for ingredient_item in ingredients:
            ingredient = get_object_or_404(Ingredient,
                                           id=ingredient_item['id'])
            if ingredient in ingredient_list:
                raise serializers.ValidationError('Ингридиенты должны '
                                                  'быть уникальными')
            ingredient_list.append(ingredient)
            if int(ingredient_item['amount']) < 0:
                raise serializers.ValidationError({
                    'ingredients': ('Убедитесь, что значение количества '
                                    'ингредиента больше 0')
                })
        data['ingredients'] = ingredients
        return data

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            CountOfIngredient.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
            )

    def create(self, validated_data):
        image = validated_data.pop('image')
        context = self.context['request']
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data, author=self.context.get('request').user)
        tags_data = self.initial_data.get('tags')
        recipe.tags.set(tags_data)
        self.create_ingredients(ingredients_data, recipe)
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


class SimpleRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')