from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from User.models import CustomUser, Trip, TripPhoto, CustomUserProfile


class TripsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = ['id','place','date','note','latitude','longitude']
        read_only_fields = ['id']

class TripPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripPhoto
        fields = ['id','image_url','uploaded_at']

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password')
        extra_kwargs = {
            'password': {'write_only': True}
        }
    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['id'] = user.id
        return token


    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id' : self.user.id,
            'username': self.user.username,
            'email': self.user.email,
        }
        return data
class CustomUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUserProfile
        fields = ['is_public', 'private_share_token', 'private_token_expires_at']