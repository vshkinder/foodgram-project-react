from rest_framework import serializers


def validate_username(value):
    if value.lower() == 'me':
        raise serializers.ValidationError(
            'Использовать имя "me" в качестве username запрещено.'
        )

    return value
