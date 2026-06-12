from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "full_name", "phone", "role", "is_active", "created_at", "updated_at")
        read_only_fields = ("id", "role", "is_active", "created_at", "updated_at")


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("id", "email", "full_name", "phone", "password")
        read_only_fields = ("id",)

    def create(self, validated_data):
        # Password khong duoc luu thang; create_user se hash password bang set_password().
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)


class LoginSerializer(TokenObtainPairSerializer):
    username_field = "email"

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Them claims de cac service khac biet user id nay co email/role gi ma khong can query identity DB.
        token["email"] = user.email
        token["role"] = user.role
        token["full_name"] = user.full_name
        return token

    def validate(self, attrs):
        # SimpleJWT mac dinh dung username; project nay dang nhap bang email nen map email -> username.
        credentials = {
            "username": attrs.get("email"),
            "password": attrs.get("password"),
        }
        user = authenticate(**credentials)
        if user is None or not user.is_active:
            raise serializers.ValidationError("Invalid credentials.")
        data = super().validate(attrs)
        data["user"] = UserSerializer(user).data
        return data
