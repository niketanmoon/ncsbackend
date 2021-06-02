import requests
from django.conf import settings
from django.contrib.auth import login, authenticate, logout as django_logout
# Create your views.py here.
from django.urls import reverse
from oauth2_provider.models import RefreshToken
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from api.v1.core import serializers as core_serializers
from api.v1.core.serializers import LogoutSerializer, RefreshTokenSerializer
from core.models import User


class LoginView(APIView):
    """
    Implements an endpoint to login and get application access token and refresh token
    """

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        login_serializer = core_serializers.LoginSerializer(data=request.data)
        if not login_serializer.is_valid():
            return Response(
                {
                    "errors": login_serializer.errors,
                    "message": "Email or password is invalid",
                },
                status=400,
            )
        email = login_serializer.validated_data.get("email")
        password = login_serializer.validated_data.get("password")
        user_objects = User.objects.filter(email=email)
        if user_objects.exists():
            user = authenticate(request, email=email, password=password)
            if user is None:
                return Response({"message": "Email or Password is invalid"}, status=400)
            data = {
                "username": email,
                "password": password,
                "grant_type": "password",
                "client_id": settings.DESKTOP_CLIENT_ID,
                "client_secret": settings.CLIENT_SECRETS.get(
                    settings.DESKTOP_CLIENT_ID
                ),
            }
            login_data = requests.post(
                f"{settings.SITE_DOMAIN}" + reverse("api:v1:core:auth:token"), data=data
            )
            if login_data.status_code != 200:
                return Response({"message": "Email or Password is invalid"}, status=400)
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")

            login_data_dict = {"user_id": user.id}
            login_data_dict.update(login_data.json())
            return Response(
                {"message": "Successfully Logged in!", "login_data": login_data_dict},
                status=200,
            )
        else:
            return Response({"message": "Email or Password is invalid"}, status=400)


class SignUpView(APIView):
    """
    Implements an endpoint to logout and revoke application access token and refresh token
    """

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        signup_serializer = core_serializers.SignUpSerializer(data=request.data)
        if not signup_serializer.is_valid():
            return Response(
                {"errors": signup_serializer.errors, "message": "Signup Error"},
                status=400,
            )
        password = signup_serializer.validated_data.get("password")
        first_name = signup_serializer.validated_data.get("first_name")
        last_name = signup_serializer.validated_data.get("last_name")
        email = signup_serializer.validated_data.get("email")
        mobile_number = signup_serializer.validated_data.get("mobile_number")
        user = User.objects.create_user(
            email=email,
            username=email,
            mobile=mobile_number,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        data = {
            "username": email,
            "password": password,
            "grant_type": "password",
            "client_id": settings.DESKTOP_CLIENT_ID,
            "client_secret": settings.CLIENT_SECRETS.get(settings.DESKTOP_CLIENT_ID),
        }
        login_data = requests.post(
            f"{settings.SITE_DOMAIN}" + reverse("api:v1:core:auth:token"), data=data
        )
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")

        login_data_dict = {"user_id": user.id}
        login_data_dict.update(login_data.json())
        return Response(
            {"message": "Successfully Logged in!", "login_data": login_data_dict},
            status=200,
        )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def logout(request):
    logout_serializer = LogoutSerializer(data=request.data)

    if logout_serializer.is_valid():
        refresh_token_instance = RefreshToken.objects.filter(
            access_token__token=request.data.get("access_token")
        ).first()

        headers = {"Authorization": f"Bearer {request.data.get('access_token')}"}
        data = {
            "client_id": request.data.get("client_id"),
            "client_secret": settings.CLIENT_SECRETS.get(request.data.get("client_id")),
            "token": request.data.get("access_token"),
        }
        response = requests.post(
            f"{settings.SITE_DOMAIN}" + reverse("api:v1:core:auth:revoke_token"),
            data=data,
            headers=headers,
        )

        if refresh_token_instance:
            refresh_token_instance.delete()

        django_logout(request)

        return Response({"message": "Successfully Logged out!", "detail": response})

    return Response(
        {
            "errors": logout_serializer.errors,
            "message": "client_id or token is invalid",
        },
        status=400,
    )


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def refresh_token(request):
    refresh_token_serializer = RefreshTokenSerializer(data=request.data)

    if refresh_token_serializer.is_valid():
        refresh_token_instance = RefreshToken.objects.filter(
            token=request.data.get("refresh_token"),
            application__client_id=request.data.get("client_id"),
        ).first()

        if refresh_token_instance:
            user = refresh_token_instance.user

            data = {
                "client_id": request.data.get("client_id"),
                "client_secret": settings.CLIENT_SECRETS.get(
                    request.data.get("client_id")
                ),
                "refresh_token": request.data.get("refresh_token"),
                "grant_type": "refresh_token",
            }
            response = requests.post(
                f"{settings.SITE_DOMAIN}" + reverse("api:v1:core:auth:token"),
                data=data,
            )

            refresh_token_instance.delete()

            login_data_dict = {"user_id": user.id}
            login_data_dict.update(response.json())
            return Response(
                {
                    "message": "Successfully exchanged refresh token!",
                    "login_data": login_data_dict,
                }
            )

    return Response(
        {
            "errors": refresh_token_serializer.errors,
            "message": "token or client_id or grant_type is invalid",
        },
        status=400,
    )
