from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Subscribe, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
    )
    fields = (
        'email',
        'password',
        'username',
        'first_name',
        'last_name',
        ('last_login', 'date_joined',)
    )
    fieldsets = []
    search_fields = ('username', 'email',)
    list_filter = ('username', 'email',)
    ordering = ('username', )
    readonly_fields = ('last_login', 'date_joined',)
    empty_value_display = '-пусто-'


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    search_fields = ('user', )
    list_filter = ('user',)
    empty_value_display = '-пусто-'
