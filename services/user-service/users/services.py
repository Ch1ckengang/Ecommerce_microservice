from django.contrib.auth import get_user_model
from rest_framework.exceptions import NotFound

User = get_user_model()


class UserService:
    @staticmethod
    def register_user(validated_data):
        password = validated_data.pop("password")
        validated_data.pop("password_confirm")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    @staticmethod
    def get_user(user_id: int):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist as exc:
            raise NotFound("User not found.") from exc

    @staticmethod
    def update_user(user, validated_data):
        for field, value in validated_data.items():
            setattr(user, field, value)
        user.save()
        return user
