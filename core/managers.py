import sys
import six

from django.contrib.auth.base_user import BaseUserManager
from django.db import IntegrityError, transaction

from utils import generate_referral_code_for_user


class UserManager(BaseUserManager):
    def get_user(self, mobile=None, email=None):
        kwargs = {}

        if email:
            kwargs["email"] = email

        if mobile:
            kwargs["mobile"] = mobile

        if not kwargs:
            raise self.model.DoesNotExist

        return self.get(**kwargs)

    def get_or_create_user(self, email, referred_by_code, mobile=None, **defaults):
        try:
            return self.get_user(mobile=mobile), False
        except self.model.DoesNotExist:
            try:
                return self.get_user(email=email), False
            except self.model.DoesNotExist:
                try:
                    return (
                        self.create_user(
                            mobile=mobile,
                            email=email,
                            referred_by_code=referred_by_code,
                            **defaults,
                        ),
                        True,
                    )
                except IntegrityError:
                    exc_info = sys.exc_info()
                    try:
                        return self.get_user(mobile=mobile), False
                    except self.model.DoesNotExist:
                        six.reraise(*exc_info)

    @transaction.atomic
    def create_user(
        self, mobile=None, email=None, password=None, referred_by_code=None, **kwargs
    ):
        if not (mobile or email):
            raise TypeError("Need at least mobile or email")

        kwargs.setdefault("is_staff", False)
        kwargs.setdefault("is_superuser", False)
        email = self.normalize_email(email) or None
        user = self.create(mobile=mobile or None, email=email, **kwargs)
        if password:
            user.set_password(password)

        user.referred_by_referral_code = referred_by_code

        code = generate_referral_code_for_user()
        # Check if the code is unique
        user_objects = self.filter(referred_to_referral_code=code)
        if user_objects.exists():
            raise Exception("Referral code already exists")

        user.referred_to_referral_code = code
        user.save()

        print(
            "Referral Code for the user %s is %s"
            % (user.get_full_name(), user.referred_to_referral_code)
        )
        return user

    def create_superuser(self, username, email, password, first_name, **kwargs):
        """Creates and saves a superuser with the given email and password."""
        kwargs["is_staff"] = True
        kwargs["is_superuser"] = True

        super_user = self.create_user(
            email=email,
            password=password,
            first_name=first_name,
            username=username,
            **kwargs,
        )

        return super_user
