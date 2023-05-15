import re

from django.core.exceptions import ValidationError


def validate_user(value):
    if not re.fullmatch(r'^[\w.@+-]+\Z', value):
        raise ValidationError('Ожидается ввод корректного имени пользователя.')
    if value == 'me':
        raise ValidationError('Использование имени me запрещено.')
