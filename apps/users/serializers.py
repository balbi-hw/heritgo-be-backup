from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "user_id",
            "username",
            "email",
            "nickname",
            "password",
            "password_confirm",
            "is_agree_ads",
            "is_agree_privacy",
        ]
        read_only_fields = [
            "user_id",
        ]

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError(
                {
                    "password_confirm": "비밀번호가 일치하지 않습니다."
                }
            )
        
        if not data.get("is_agree_privacy"):
            raise serializers.ValidationError(
                {
                    "is_agree_privacy": "개인정보 처리방침 동의는 필수입니다."
                }
            )
        
        return data
    
    def create(self, validated_data):
        validated_data.pop("password_confirm")

        password = validated_data.pop("password")

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        return user