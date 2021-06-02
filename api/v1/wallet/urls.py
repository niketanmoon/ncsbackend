from django.urls import path, include

from api.v1.wallet import views as wallet_views

urlpatterns = [
    path("add-money/", wallet_views.AddMoneyView.as_view(), name="add_money"),
    path("transfer-money/", wallet_views.TransferMoney.as_view(), name="transfer_money"),
    path("get-transactions", wallet_views.Transactions.as_view(), name="transactions"),
]