from django.shortcuts import get_object_or_404
from recipes.models import Ingredient, IngredientRecipe
from rest_framework import response, status


def create_obj(request, serializer_name, instance):
    serializer = serializer_name(
        data={'user': request.user.id, 'recipe': instance.id, },
        context={'request': request}
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return response.Response(serializer.data, status=status.HTTP_201_CREATED)


def delete_obj(request, model_name, instance, err_msg):
    if not model_name.objects.filter(user=request.user,
                                     recipe=instance).exists():
        return response.Response(
            {'errors': err_msg},
            status=status.HTTP_400_BAD_REQUEST)
    model_name.objects.filter(
        user=request.user, recipe=instance).delete()
    return response.Response(
        {'successfully': 'удалено.'},
        status=status.HTTP_204_NO_CONTENT)


def add_ingredients(ingredients, recipe):
    ingredient_list = []
    for ingredient in ingredients:
        current_ingredient = get_object_or_404(
            Ingredient, id=ingredient.get('id'))
        amount = ingredient.get('amount')
        ingredient_list.append(
            IngredientRecipe(
                recipe=recipe,
                ingredient=current_ingredient,
                amount=amount
            )
        )
    IngredientRecipe.objects.bulk_create(ingredient_list)
