import re

from django.core.exceptions import ValidationError
from rest_framework import serializers


def validate_username(value):
    if not re.match(r'^[a-zA-Z0-9_]+$', value):
        raise serializers.ValidationError(
            'Имя пользователя должно содержать'
            'только латинские буквы, цифры и подчеркивания.'
        )
    if value == 'me':
        raise serializers.ValidationError(
            'Имя пользователя "me" недопустимо.'
        )
    return value
