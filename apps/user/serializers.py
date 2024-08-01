from djoser.serializers import PasswordResetConfirmSerializer
from djoser.serializers import UserCreateSerializer
from urllib.parse import urlparse
from rest_framework import serializers
from django.conf import settings

from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserSerializer(UserCreateSerializer):
    picture = serializers.ImageField(required=False)

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = [
            "id",
            "email",
            "username",
            "picture",
            "first_name",
            "last_name",
            "is_online",
            "is_active",
            "is_staff",
            "role",
            "verified",
            "date_joined",
            "updated_at",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.picture:
            representation["picture"] = self.get_base_url(instance.picture.url)
        return representation

    def get_base_url(self, url):
        parsed_url = urlparse(url)
        develop_url = f"http:localhost:9000{parsed_url.path}"
        production_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        base_url = develop_url if settings.DEBUG else production_url
        return base_url


class CustomPasswordResetConfirmSerializer(PasswordResetConfirmSerializer):
    def build_password_reset_confirm_url(self, uid, token):
        url = f"?forgot_password_confirm=True&uid={uid}&token={token}"
        return url
