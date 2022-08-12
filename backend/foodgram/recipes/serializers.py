import traceback

from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from users.models import CustomUser

from .models import (CountOfIngredient, Favorite, Ingredient, Recipe, Shoplist,
                     Tag)


class GetIsSubscribedMixin:

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return user.follower.filter(author=obj).exists()


class RecipeUserSerializer(
        GetIsSubscribedMixin,
        serializers.ModelSerializer):

    is_subscribed = serializers.SerializerMethodField(
        read_only=True)

    class Meta:
        model = CustomUser
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed')


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


class RecipeWriteSerializer(serializers.ModelSerializer):
    image = Base64ImageField(
        max_length=None,
        use_url=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all())
    ingredients = CountOfIngredientSerializer(
        many=True)

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = ('author',)

    def validate(self, data):
        ingredients = data['ingredients']
        ingredient_list = []
        for items in ingredients:
            ingredient = Ingredient.objects.get(id=items['id'])
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    'Ингредиент должен быть уникальным!')
            ingredient_list.append(ingredient)
        tags = data['tags']
        if not tags:
            raise serializers.ValidationError(
                'Добавьте хотя бы один тэг!')
        for tag_name in tags:
            if not Tag.objects.filter(name=tag_name).exists():
                raise serializers.ValidationError(
                    f'Тэга {tag_name} не существует!')
        return data

    def validate_cooking_time(self, cooking_time):
        if int(cooking_time) < 1:
            raise serializers.ValidationError(
                'Время приготовления >= 1!')
        return cooking_time

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Мин. 1 ингредиент в рецепте!')
        for ingredient in ingredients:
            if int(ingredient.get('amount')) < 1:
                raise serializers.ValidationError(
                    'Количество ингредиента >= 1!')
        return ingredients

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            CountOfIngredient.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'), )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            self.create_ingredients(ingredients, instance)
        if 'tags' in validated_data:
            instance.tags.set(
                validated_data.pop('tags'))
        return super().update(
            instance, validated_data)

    def to_representation(self, instance):
        return CountOfIngredient(
            instance,
            context={
                'request': self.context.get('request')
            }).data


class RecipeReadSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    tags = TagSerializer(
        many=True,
        read_only=True)
    author = RecipeUserSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault())
    ingredients = CountOfIngredientSerializer(
        many=True,
        required=True,
        source='recipe')
    is_favorited = serializers.BooleanField(
        read_only=True)
    is_in_shopping_cart = serializers.BooleanField(
        read_only=True)

    class Meta:
        model = Recipe
        fields = '__all__'

#class RecipeSerializer(serializers.ModelSerializer):
#    name = serializers.CharField(
#        required=True,
#    )
#    author = AuthorSerializer(read_only=True)
#    tags = TagSerializer(read_only=True, many=True)
#    ingredients = CountOfIngredientSerializer(
#        many=True, source='recipe_ingredients'
#    )
#    image = Base64ImageField(
#        max_length=None, use_url=True,
#    )
#    text = serializers.CharField()
#    cooking_time = serializers.IntegerField(max_value=32767, min_value=1)
#    is_favorited = serializers.SerializerMethodField()
#    is_in_shopping_cart = serializers.SerializerMethodField()
#
#    class Meta:
#        model = Recipe
#        exclude = ('pub_date',)
#
#    def get_status_func(self, data):
#        request = self.context.get('request')
#        if request is None or request.user.is_anonymous:
#            return False
#        try:
#            user = self.context.get('request').user
#        except:
#            user = self.context.get('user')
#        callname_function = format(traceback.extract_stack()[-2][2])
#        if callname_function == 'get_is_favorited':
#            init_queryset = Favorite.objects.filter(recipe=data.id, user=user)
#        elif callname_function == 'get_is_in_shopping_cart':
#            init_queryset = Shoplist.objects.filter(recipe=data, user=user)
#        if init_queryset.exists():
#            return True
#        return False
#
#    def get_is_favorited(self, data):
#        return self.get_status_func(data)
#
#    def get_is_in_shopping_cart(self, data):
#        return self.get_status_func(data)
#
#    def create(self, validated_data):
#        context = self.context['request']
#        ingredients = validated_data.pop('recipe_ingredients')
#        try:
#            recipe = Recipe.objects.create(
#                **validated_data,
#                author=self.context.get('request').user
#            )
#        except IntegrityError as err:
#            pass
#        tags_set = context.data['tags']
#        for tag in tags_set:
#            Tag.objects.create(
#                recipe=recipe,
#                tag=Tag.objects.get(id=tag)
#            )
#        ingredients_set = context.data['ingredients']
#        for ingredient in ingredients_set:
#            ingredient_model = Ingredient.objects.get(id=ingredient['id'])
#            CountOfIngredient.objects.create(
#                recipe=recipe,
#                ingredient=ingredient_model,
#                amount=ingredient['amount'],
#            )
#        return recipe
#
#    def update(self, instance, validated_data):
#        context = self.context['request']
#        ingredients = validated_data.pop('recipe_ingredients')
#        tags_set = context.data['tags']
#        recipe = instance
#        instance.name = validated_data.get('name', instance.name)
#        instance.text = validated_data.get('text', instance.text)
#        instance.cooking_time = validated_data.get(
#            'cooking_time', instance.cooking_time
#        )
#        instance.image = validated_data.get('image', instance.image)
#        instance.save()
#        instance.tags.set(tags_set)
#        CountOfIngredient.objects.filter(recipe=instance).delete()
#        ingredients_req = context.data['ingredients']
#        for ingredient in ingredients_req:
#            ingredient_model = Ingredient.objects.get(id=ingredient['id'])
#            CountOfIngredient.objects.create(
#                recipe=recipe,
#                ingredient=ingredient_model,
#                amount=ingredient['amount'],
#            )
#        return instance
#
#    def to_representation(self, instance):
#        response = super(RecipeSerializer, self).to_representation(instance)
#        if instance.image:
#            response['image'] = instance.image.url
#        return response


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
        model = Favorite
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
