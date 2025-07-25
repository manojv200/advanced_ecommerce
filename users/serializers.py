from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import TblUser


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    access_token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)

    class Meta:
        model = TblUser
        fields = ['username', 'email', 'password', 'phone', 'address', 'access_token', 'refresh_token']

    def create(self, validated_data):
        user = TblUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            phone=validated_data['phone']
        )

        refresh = RefreshToken.for_user(user)
        user.refresh_token = refresh
        user.access_token = refresh.access_token

        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TblUser
        fields = ['username', 'email', 'phone', 'address']
