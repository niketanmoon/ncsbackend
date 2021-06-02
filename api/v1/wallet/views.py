from rest_framework.views import APIView
from rest_framework import permissions
from api.v1.wallet import serializers as wallet_serializers
from wallet import models as wallet_models
from core import models as core_models
from rest_framework.response import Response
import uuid


class AddMoneyView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request):
        add_serializer = wallet_serializers.AddMoneySerializer(data=request.data)
        if not add_serializer.is_valid():
            return Response(
                {
                    "errors": add_serializer.errors,
                    "message": "Cannot add amount",
                },
                status=400
            )
        transaction_amount = add_serializer.validated_data.get('amount')
        transaction_id = uuid.uuid4()

        # create wallet transaction
        wallet_models.Wallet.objects.create(
            transaction_id=transaction_id,
            transferred_by=self.request.user,
            transaction_status=wallet_models.Wallet.SUCCESS,
            transaction_type=wallet_models.Wallet.CREDIT,
            transaction_amount=transaction_amount
        )

        # Add money to the user wallet
        user = self.request.user
        user.wallet_amount += transaction_amount
        user.save(update_fields=["wallet_amount"])
        return Response({
            "message": "Amount is Credited",
            "amount": user.wallet_amount
        }, status=200)


class TransferMoney(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request):
        transfer_serializer = wallet_serializers.TransferMoneySerializer(data=request.data)
        if not transfer_serializer.is_valid():
            return Response({
                "errors": transfer_serializer.errors,
                "message": "Cannot add amount",
            }, status=400)

        transaction_amount = transfer_serializer.validated_data.get("amount")
        if transaction_amount > self.request.user.wallet_amount:
            return Response({
                "message": "Not sufficient amount to transfer"
            }, status=400)
        email = transfer_serializer.validated_data.get("transferred_to_email")
        transferred_to_user_objects = core_models.User.objects.filter(email=email)
        if transferred_to_user_objects.exists():
            transferred_to_user = transferred_to_user_objects.last()
            # Create wallet transaction for adding into another user
            wallet_models.Wallet.objects.create(
                transaction_id=uuid.uuid4(),
                transferred_by=self.request.user,
                transferred_to=transferred_to_user,
                transaction_type=wallet_models.Wallet.DEBIT,
                transaction_status=wallet_models.Wallet.SUCCESS,
                transaction_reason=wallet_models.Wallet.TRANSFER_MONEY_REASON,
                transaction_amount=transaction_amount
            )

            # Now add the wallet amount to transferred to user
            transferred_to_user.wallet_amount += transaction_amount
            transferred_to_user.save(update_fields=["wallet_amount"])

            # Now deduct the amount from transferred by user
            self.request.user.wallet_amount -= transaction_amount

            return Response({
                "message": "Money transferred",
                "amount": self.request.user.wallet_amount
            }, status=200)
        else:
            return Response({
                "message": "Email not found"
            }, status=400)


class Transactions(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request):
        results = []
        obj = wallet_models.Wallet.objects.filter(
            transferred_by=self.request.user
        )
        for transaction in obj:
            if transaction in results:
                continue
            else:
                results.append(transaction.get_wallet_dict())
        return Response({
            "results": results,
            "message": "Success"
        }, status=200)
