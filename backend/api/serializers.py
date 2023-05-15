import base64
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers, validators
from django.core.files.base import ContentFile
from recipes.models import (Tag, Ingredient, Recipe,
                            Favorite, IngredientRecipe,
                            ShoppingCart)
from users.models import User, Subscribe
from django.db import transaction
from api.utils import add_ingredients


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class Us3rSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscribe.objects.filter(user=obj).exists()


class CreateUserSerializer(UserCreateSerializer):
    """ Сериализатор для создания ползателя """

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data.get("username"),
            email=validated_data.get("email"),
            first_name=validated_data.get("first_name"),
            last_name=validated_data.get("last_name")
        )
        user.set_password(validated_data.get("password"))
        user.save()
        return user


class RecipeSmallSerializer(serializers.ModelSerializer):
    """ Сериализатор для представления """
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    """ Сериализатор для вывода после подписки """

    recipes = RecipeSmallSerializer(read_only=True, many=True)
    recipes_count = serializers.IntegerField(source='author.recipes.count',
                                             read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )
        read_only_fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscribe.objects.filter(user=obj).exists()


class TagSerializer(serializers.ModelSerializer):
    """ Сериализатор для тегов """

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """ Сериализатор для ингредиентов """

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """ Сериализатор для количества ингредиента """
    id = serializers.ReadOnlyField(source='ingredient.id', read_only=True)
    name = serializers.ReadOnlyField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = IngredientRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class ReadOnlyRecipeSerializer(serializers.ModelSerializer):
    """ Рецепт чтение """
    tags = TagSerializer(many=True, read_only=True)
    author = Us3rSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(
        many=True, source='ingredients_recipes', read_only=True
    )
    image = Base64ImageField(required=False)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        # fields = '__all__'
        exclude = ('pub_date', )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user,
                                       recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and ShoppingCart.objects.filter(
                    user=request.user, recipe=obj
                ).exists())


class AmountSerializer(serializers.ModelSerializer):
    """  Рецепт количество   """
    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(write_only=True, min_value=1)

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount',)


class RecipeSerializer(serializers.ModelSerializer):
    """ Рецепт создание """
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = AmountSerializer(
        many=True, source='ingredients_recipes'
    )
    image = Base64ImageField()

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get('request')
        ingredients = validated_data.pop('ingredients_recipes')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        add_ingredients(ingredients, recipe)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients_recipes')
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        IngredientRecipe.objects.filter(recipe=instance).delete()
        super().update(instance, validated_data)
        add_ingredients(ingredients, instance)
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeSmallSerializer(
            instance,
            context={'request': request}
        ).data

    class Meta:
        model = Recipe
        fields = ('ingredients',
                  'tags',
                  'image',
                  'name',
                  'text',
                  'cooking_time'
                  )


class FavoriteSerializer(serializers.ModelSerializer):
    """ Серализатор для избранных рецептов """

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

        validators = [
            validators.UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже в избранном'
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeSmallSerializer(
            instance.recipe,
            context=context
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """ Сериализатор для корзины списка покупок"""

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

        validators = [
            validators.UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Такой рецепт уже есть в списке покупок'
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeSmallSerializer(
            instance.recipe,
            context=context,
        ).data
