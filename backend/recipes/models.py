from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from foodgram import settings
from users.models import User


class Tag(models.Model):
    """ Модель для тегов """
    name = models.CharField(
        verbose_name='Название',
        max_length=20,
        unique=True
    )
    color = models.CharField(
        verbose_name='Цвет',
        max_length=16,
        unique=True
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=20,
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """ Модель для игредиентов """
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=250,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=250,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """ Модель для рецептов """
    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=200,
        null=False
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipes/image/',
        blank=True,
        null=True,
    )
    text = models.TextField(
        verbose_name='Рецепт',
        max_length=10000,
    )
    ingredients = models.ManyToManyField(
        verbose_name='Ингридиенты',
        to=Ingredient,
        through='IngredientRecipe',
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        to=Tag,
        verbose_name='Тег',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления в минутах',
        default=1,
        validators=[MinValueValidator(limit_value=1,
                    message=settings.MIN_COOK_TIME),
                    MaxValueValidator(limit_value=4500,
                    message=settings.MAX_COOK_TIME),
                    ]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    """ Модель для количества ингредиентов в рецепте """
    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_recipes',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        to=Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients_recipes',
        verbose_name='Ингридиент',
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(limit_value=1,
                    message=settings.MIN_AMOUNT_ING)],
        verbose_name='Количество ингредиентов'
    )

    class Meta:
        ordering = ('id', )
        verbose_name = 'Количество ингридиента'
        verbose_name_plural = 'Количество ингридиентов'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredients_recipe'
            )
        ]

    def __str__(self):
        return (
            f'{self.ingredient.name} - {self.amount}'
            f' {self.ingredient.measurement_unit}'
        )


class Favorite(models.Model):
    """ Модель для добавление рецептов в избранное """
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт в избранном',
    )

    class Meta:
        ordering = ('id', )
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.recipe} добавлен в избранное пользователем {self.user}'


class ShoppingCart(models.Model):
    """ Модель для корзины """
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='carts',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
        related_name='carts',
        verbose_name='Рецепт'
    )

    class Meta:
        ordering = ('-id', )
        verbose_name = 'Ингридиент в корзине'
        verbose_name_plural = 'Ингридиенты в корзине'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe_recipe_in_cart'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил в корзину {self.recipe}'
