from djoser.serializers import UserCreateSerializer
from rest_framework import serializers, validators

from recipes.models import Recipe
from recipes.serializers import RecipeSerializer

from .mixins import IsSubscribedMixin
from .models import CustomUser, Subscribe


class UserRegistrationSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = CustomUser
        fields = [
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        ]


class UserSerializer(serializers.ModelSerializer, IsSubscribedMixin):
    username = serializers.CharField(
        required=True,
        validators=[validators.UniqueValidator(
            queryset=CustomUser.objects.all()
        )]
    )

    class Meta:
        fields = [
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed'
        ]
        model = CustomUser


class UserSubscribeSerializer(serializers.ModelSerializer, IsSubscribedMixin):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField('get_recipes_count')
    username = serializers.CharField(
        required=True,
        validators=[validators.UniqueValidator(
            queryset=CustomUser.objects.all()
        )]
    )

    class Meta:
        model = CustomUser
        fields = [
            'email', 'id', 'username', 'first_name', 'last_name',
            'recipes', 'recipes_count', 'is_subscribed'
        ]

    def validate(self, data):
        author = data['subscribing']
        user = data['subscriber']
        if user == author:
            raise serializers.ValidationError(
                'Вы не можете подписаться на себя.'
            )
        if Subscribe.objects.filter(author=author, user=user).exists():
            raise serializers.ValidationError('Вы уже подписаны!')
        return data

    def create(self, validated_data):
        subscribe = Subscribe.objects.create(**validated_data)
        subscribe.save()
        return subscribe

    def get_recipes_count(self, data):
        return Recipe.objects.filter(author=data).count()

    def get_recipes(self, data):
        recipes_limit = self.context.get('request').GET.get('recipes_limit')
        recipes = (
            data.recipes.all()[:int(recipes_limit)]
            if recipes_limit else data.recipes
        )
        serializer = serializers.ListSerializer(child=RecipeSerializer())
        return serializer.to_representation(recipes)
