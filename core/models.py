import uuid as uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from core.managers import UserManager


class TrackableModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# Create your models here.
class User(AbstractUser, TrackableModel):
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name"]
    uuid = models.UUIDField(unique=True, default=uuid.uuid4)
    username = models.CharField(
        max_length=150,
        unique=False,
        null=True,
        blank=True,
        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
        validators=[AbstractUser.username_validator],
        error_messages={"unique": "A user with that username already exists."},
    )
    email = models.EmailField(
        blank=True, null=True, unique=True, db_index=True, db_column="email"
    )
    mobile = models.CharField(
        max_length=10,
        unique=True,
        db_index=True,
        db_column="mobile",
        null=True,
        blank=True,
    )
    referred_by_referral_code = models.CharField(max_length=20, null=True, blank=True)
    referred_to_referral_code = models.CharField(max_length=20)
    wallet_amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0.00
    )

    objects = UserManager()

    def get_user_dict(self):
        return {
            "email": self.email
        }