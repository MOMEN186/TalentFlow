# accounts/serializers.py
from rest_framework import serializers
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    # Expose just the Cloudinary URL on read
    profile_photo = serializers.SerializerMethodField()

    # Accept an 'image' upload mapped into the CloudinaryField
    image = serializers.ImageField(source="profile_photo", write_only=True, required=False)

    class Meta:
        model  = CustomUser
        fields = ("id", "email", "full_name", "image", "profile_photo", "password")
        extra_kwargs = {
            "password": {"write_only": True, "min_length": 8},
        }

    def get_profile_photo(self, obj):
        # obj.profile_photo.url gives the full Cloudinary URL
        return obj.profile_photo.url if obj.profile_photo else None

    def create(self, validated_data):
        photo = validated_data.pop("profile_photo", None)
        user = CustomUser.objects.create_user(**validated_data)
        if photo:
            user.profile_photo = photo
            user.save()
        return user

    def update(self, instance, validated_data):
        pwd = validated_data.pop("password", None)
        if pwd:
            instance.set_password(pwd)

        photo = validated_data.pop("profile_photo", None)
        if photo is not None:
            instance.profile_photo = photo

        for attr, val in validated_data.items():
            setattr(instance, attr, val)

        instance.save()
        return instance
