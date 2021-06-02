from rest_framework import serializers
from django.core.validators import RegexValidator


class AddMoneySerializer(serializers.Serializer):
    amount = serializers.DecimalField(
        required=True,
        decimal_places=2,
        max_digits=8
    )


class TransferMoneySerializer(serializers.Serializer):
    amount = serializers.DecimalField(
        required=True,
        decimal_places=2,
        max_digits=8
    )
    transferred_to_email = serializers.EmailField(
        max_length=200,
        required=True,
        validators=[
            RegexValidator(
                regex=r"^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$",
                message="Invalid email address",
            )
        ],
    )