from rest_framework import serializers

from django.contrib.auth import get_user_model

from .models import MyUser

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'password', 'username')

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError('Password must be atleast 8 characters long')
        return value
    
    def validate_email(self, value):
        if not '@' in value:
            raise serializers.ValidationError('Enter valid email')
        return value
    
    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()

        return user