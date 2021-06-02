from django.urls import include, path

urlpatterns = [
    path("core/", include(("api.v1.core.urls", "api_v1_core"), namespace="core")),
    path("wallet/", include(("api.v1.wallet.urls", "api_v1_wallet"), namespace="wallet"))
]