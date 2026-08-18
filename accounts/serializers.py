from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True)

    class Meta:
        model = User
        fields =['email','password','full_name','github_id']

    def create(self,validated_data):
        return User.objects.create_user(**validated_data)

class LoginSerializer(serializers.Serializer):
    password = serializers.CharField(write_only =True)
    email = serializers.EmailField()
    
    def validate(self, attrs):
        user = authenticate(email=attrs['email'],password=attrs['password'])

        if not user:
            raise serializers.ValidationError('Invalid credentials')
        attrs['user'] = user
        return attrs