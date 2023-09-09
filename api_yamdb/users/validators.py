import re

from rest_framework import serializers


def validate_username(value):
    if not re.match(r'^[\w.@+-]+$', value):
        raise serializers.ValidationError(
            'Имя пользователя должно содержать'
            'только латинские буквы, цифры и подчеркивания.'
        )
    if value == 'me':
        raise serializers.ValidationError(
            'Имя пользователя "me" недопустимо.'
        )
    return value
