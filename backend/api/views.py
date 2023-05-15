from django.db.models import Sum
from django.shortcuts import get_object_or_404, HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework import permissions, response, status, viewsets
from djoser import views
from recipes import models as recipes_models
from users.models import User, Subscribe
from api import filters
from api.permissions import IsAdminOrAuthor
from api.pagination import RecipePagination
from api import serializers as api_serializers
from api.utils import create_obj, delete_obj


class UserViewSet(views.UserViewSet):
    """ Вьюсет для работы с пользователями и подписками """
    queryset = User.objects.all()
    serializer_class = api_serializers.Us3rSerializer
    pagination_class = RecipePagination

    @action(
        detail=True, methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, **kwargs):
        user = request.user
        author_id = self.kwargs.get('id')
        author = get_object_or_404(User, id=author_id)
        if request.method == 'POST' and user.is_authenticated:
            if Subscribe.objects.filter(user=user, author=author).exists():
                return response.Response(
                    'Такая подписка уже существует',
                    status=status.HTTP_400_BAD_REQUEST)
            serializer = api_serializers.SubscribeSerializer(
                author,
                data=request.data,
                context={"request": request},)
            serializer.is_valid(raise_exception=True)
            Subscribe.objects.create(user=user, author=author)
            return response.Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            subscription = get_object_or_404(
                Subscribe,
                user=user,
                author=author,
            )
            subscription.delete()
            return response.Response(
                {"errors": "отписка"}, status=status.HTTP_204_NO_CONTENT
            )

    @action(
        detail=False,
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(subscribing__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = api_serializers.SubscribeSerializer(
            pages,
            many=True,
            context={'request': request},
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Вьюсет для тегов
    Доступен всем только для чтения.
    """
    queryset = recipes_models.Tag.objects.all()
    serializer_class = api_serializers.TagSerializer
    permission_classes = (permissions.AllowAny, )


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Вьюсет для отображения ингредиентов.
    Доступен всем только для чтения.
    """
    queryset = recipes_models.Ingredient.objects.all()
    serializer_class = api_serializers.IngredientSerializer
    permission_classes = (permissions.AllowAny, )
    filter_backends = (filters.IngredientSearchFilter, )
    search_fields = ('^name', )


class FavoriteViewSet(viewsets.ModelViewSet):
    """ Вьюсет для избраного """
    queryset = recipes_models.Favorite.objects.all()
    serializer_class = api_serializers.FavoriteSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """ Вьюсет для рецептов """
    queryset = recipes_models.Recipe.objects.all()
    permission_classes = (IsAdminOrAuthor, )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.RecipeFilter
    pagination_class = RecipePagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return api_serializers.ReadOnlyRecipeSerializer
        return api_serializers.RecipeSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated, ]
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(recipes_models.Recipe, id=pk)
        if request.method == 'POST':
            return create_obj(
                request, api_serializers.FavoriteSerializer, recipe)
        err_msg = 'Такого рецепта нет в избранном.'
        return delete_obj(
            request, recipes_models.Favorite, recipe, err_msg)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated, ]
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(recipes_models.Recipe, id=pk)
        if request.method == 'POST':
            return create_obj(
                request, api_serializers.ShoppingCartSerializer, recipe)
        err_msg = 'Этого рецепта в списке покупок нет.'
        return delete_obj(
            request, recipes_models.ShoppingCart, recipe, err_msg)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated, ]
    )
    def download_shopping_cart(self, request):
        ingredients = recipes_models.IngredientRecipe.objects.filter(
            recipe__carts__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            ingredient_amount=Sum('amount')
        ).order_by(
            'ingredient__name'
        )
        shopping_list = ['Список покупок:\n']
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            amount = ingredient['ingredient_amount']
            unit = ingredient['ingredient__measurement_unit']
            shopping_list.append(f'\n{name} - {amount} {unit}')
        filename = 'shopping_cart.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
