from django.urls import path, include

from api.v1.core import views as core_views

urlpatterns = [
    path(
        "auth/",
        include(("drf_social_oauth2.urls", "api_v1_core_auth"), namespace="auth"),
    ),
    path("login/", core_views.LoginView.as_view(), name="login"),
    path("signup/", core_views.SignUpView.as_view(), name="signup"),
    path("logout/", core_views.logout, name="logout"),
    path("refresh-token/", core_views.refresh_token, name="refresh_token"),
]