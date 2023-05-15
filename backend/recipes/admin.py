from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import (
    Recipe, Tag, Ingredient,
    Favorite, IngredientRecipe, ShoppingCart)

admin.site.site_header = 'Администрирование Foodgram'
admin.site.index_title = 'Панель администратора Foodgram'


@admin.register(IngredientRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    fields = (
        'recipe',
        'ingredient',
        'amount',
    )
    search_fields = ('ingredient', 'recipe',)


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    # min_num = 1
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'color',
        'slug',
    )
    list_editable = (
        'color',
    )
    search_fields = ('name', 'slug',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    filter_horizontal = ('tags', )
    list_display = (
        'name',
        'author',
        'get_image',
        'get_ingredients',
        'in_favorites_amount',
        'cooking_time',
    )
    search_fields = ('author', 'name', )
    list_filter = ('name', 'author', 'tags', )
    autocomplete_fields = ('ingredients', )
    inlines = (IngredientRecipeInline, )
    readonly_fields = ('in_favorites_amount', )
    empty_value_display = '-пусто-'

    @admin.display(description='в избраном')
    def in_favorites_amount(self, object):
        return object.favorites.count()

    @admin.display(description='Миниатюра')
    def get_image(self, object):
        if object.image:
            return mark_safe(
                f'<img src={object.image.url} width="80" height="45">')
        return 'Нет изображения'

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, object):
        return [
            name['name'] for name in object.ingredients.all().values('name')]


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    search_fields = ('^name', )
    list_filter = ('name', )
    empty_value_display = '-пусто-'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user', )
    list_filter = ('user',)
    empty_value_display = '-пусто-'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    search_fields = ('user', 'recipe')
    empty_value_display = '-пусто-'
