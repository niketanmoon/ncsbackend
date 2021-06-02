from django.core.validators import RegexValidator
from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(
        max_length=200,
        required=True,
        validators=[
            RegexValidator(
                regex=r"^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$",
                message="Invalid email address",
            )
        ],
    )
    password = serializers.CharField(max_length=500, required=True)


class SignUpSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=200, required=True)
    last_name = serializers.CharField(max_length=200, required=False)
    email = serializers.EmailField(
        max_length=200,
        required=True,
        validators=[
            RegexValidator(
                regex=r"^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$",
                message="Invalid email address",
            )
        ],
    )
    password = serializers.CharField(max_length=500, required=True)
    confirm_password = serializers.CharField(max_length=500, required=True)
    mobile_number = serializers.CharField(
        max_length=10, required=False, allow_blank=True
    )

    def validate(self, data):
        data = super().validate(data)
        from core.models import User

        if "email" in data and User.objects.filter(email=data.get("email")).exists():
            raise serializers.ValidationError("User with this email already exists")
        if (
            "mobile_number" in data
            and User.objects.filter(mobile=data.get("mobile_number")).exists()
        ):
            raise serializers.ValidationError("User with this mobile already exists")
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Password does not match")
        return data


class LogoutSerializer(serializers.Serializer):
    access_token = serializers.CharField(max_length=500, required=True)
    client_id = serializers.CharField(max_length=255, required=True)


class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(max_length=500, required=True)
    client_id = serializers.CharField(max_length=255, required=True)
    grant_type = serializers.CharField(max_length=255, required=True)

    def validate(self, data):
        data = super().validate(data)

        if data.get("grant_type") != "refresh_token":
            raise serializers.ValidationError("grant_type should be refresh_token")

        return data
