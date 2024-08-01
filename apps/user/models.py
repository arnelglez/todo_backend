from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)

from django.utils.translation import gettext_lazy as _

from djoser.signals import user_registered
import uuid, re


class UserAccountManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password, **extra_fields):
        user = self.create_user(email, password, **extra_fields)
        user.is_superuser = True
        user.is_staff = True
        user.role = "owner"
        user.verified = True
        user.save(using=self._db)

        return user


class UserAccount(AbstractBaseUser, PermissionsMixin):
    CHOISE_ROLE = (
        ("customer", "Customer"),
        ("moderator", "Moderator"),
        ("admin", "Admin"),
        ("owner", "Owner"),
    )

    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    email = models.EmailField(unique=True, verbose_name=_("Email"))
    username = models.CharField(max_length=100, unique=True, verbose_name=_("Username"))
    phone = models.CharField(
        max_length=20, verbose_name=(_("Phone")), blank=True, null=True
    )

    # mercado_pago_id = models.CharField(max_length=100, blank=True, null=True)
    # mercado_pago_user_id = models.CharField(max_length=100, blank=True, null=True)
    # mercado_pago_merchant_id = models.CharField(max_length=100, blank=True, null=True)
    # mercado_pago_client_id = models.CharField(max_length=100, blank=True, null=True)

    picture = models.ImageField(
        default="media/users/user_default_profile.png",
        upload_to="media/users/pictures/",
        blank=True,
        null=True,
        verbose_name=(_("Picture")),
    )

    first_name = models.CharField(max_length=100, verbose_name=(_("First Name")))
    last_name = models.CharField(max_length=100, verbose_name=(_("Last Name")))

    is_online = models.BooleanField(default=False, verbose_name=(_("Is Online")))

    is_active = models.BooleanField(default=True, verbose_name=(_("Is Active")))
    is_staff = models.BooleanField(default=False, verbose_name=(_("Is Staff")))

    role = models.CharField(
        max_length=20, choices=CHOISE_ROLE, default="customer", verbose_name=(_("Role"))
    )
    verified = models.BooleanField(default=False, verbose_name=(_("Verified")))

    date_joined = models.DateTimeField(auto_now_add=True, verbose_name=(_("Joined at")))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=(_("Updated at")))

    objects = UserAccountManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email


# def post_user_registered(request, user, *args, **kwargs):
#     # 1. Definir usuario que ser registra
#     user = user
#     customer_data = {
#         "email": user.email,
#     }
#     customer_response = sdk.customer().create(customer_data)
#     customer = customer_response["response"]

#     # Save Customer ID in Django DB
#     user.mercado_pago_id = customer["id"]
#     user.mercado_pago_user_id = customer["user_id"]
#     user.mercado_pago_merchant_id = customer["merchant_id"]
#     user.mercado_pago_client_id = customer["client_id"]
#     user.save()

#     # print(
#     #     f"""
#     #     Mercado pago Customer Created {customer}
#     #     """
#     # )


# user_registered.connect(post_user_registered)
