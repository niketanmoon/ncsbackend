import uuid

from django.db import models

from core import models as core_models


# Create your models here.


class Wallet(core_models.TrackableModel):
    CREDIT, DEBIT = "CREDIT", "DEBIT"
    PENDING, IN_PROGRESS, FAILED, SUCCESS = "P", "I", "F", 'S'
    ADD_MONEY_REASON = "Added money through bank"
    TRANSFER_MONEY_REASON = "Added money through transfer by another user"
    DECLINED_REASON = "Transaction was declined"

    TRANSACTION_TYPE = {
        CREDIT: "CREDIT",
        DEBIT: "DEBIT",
    }.items()

    TRANSACTION_STATUS = {
        PENDING: "P",
        IN_PROGRESS: "I",
        FAILED: "F",
        SUCCESS: "S"
    }.items()

    TRANSACTION_REASON = {
        ADD_MONEY_REASON: "Added money through bank",
        TRANSFER_MONEY_REASON: "Added money through transfer by another user",
        DECLINED_REASON: "Transaction was declined"
    }.items()

    transaction_id = models.UUIDField(unique=True, default=uuid.uuid4)
    transferred_by = models.ForeignKey(
        'core.User',
        on_delete=models.PROTECT,
        related_name="transferred_by"
    )
    transferred_to = models.ForeignKey(
        'core.User',
        on_delete=models.PROTECT,
        related_name="transferred_to",
        blank=True,
        null=True
    )
    transaction_type = models.CharField(
        max_length=50,
        choices=TRANSACTION_TYPE,
        default=CREDIT,
    )
    transaction_status = models.CharField(
        max_length=50,
        choices=TRANSACTION_STATUS,
        default=PENDING
    )
    transaction_reason = models.CharField(
        max_length=200,
        choices=TRANSACTION_REASON,
        default=ADD_MONEY_REASON
    )
    transaction_amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0.00
    )

    def get_wallet_dict(self):

        return {
            "transaction_id": self.transaction_id,
            "transferred_to": self.transferred_to.get_user_dict() if self.transferred_to else {},
            "transaction_type": self.transaction_type,
            "transaction_status": self.transaction_status,
            "transaction_amount": self.transaction_amount,
            "transaction_reason": self.transaction_reason,
            "transaction_date": self.created_on.strftime("%m/%d/%Y, %H:%M:%S")
        }