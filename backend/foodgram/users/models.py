from django.contrib.auth.models import AbstractUser
from django.db import models
from users.validators import validate_user


class User(AbstractUser):
    """ Модель пользователя """

    email = models.EmailField(
        max_length=254,
        verbose_name='E-mail',
        unique=True,
        help_text='укажите e-mail',
    )
    username = models.CharField(
        max_length=150,
        verbose_name='login',
        help_text='укажите логин',
        unique=True,
        validators=[validate_user, ]
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя',
        help_text='Введите ваше имя')
    last_name = models.CharField(
        max_length=150,
        verbose_name='Введите вашу фамилию',
    )
    password = models.CharField(
        'Пароль',
        max_length=150,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
        'password',
    ]

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email


class Subscribe(models.Model):
    """ Модель подписок """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик',
        help_text='Подписчик',
        null=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribing',
        verbose_name='Автор',
        help_text='Автор',
        null=True
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique subscribe'
            )
        ]

    def __str__(self):
        return f'{self.user.username} - {self.author.username}'
