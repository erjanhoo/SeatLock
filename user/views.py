from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from django.db import transaction
from django.utils import timezone
from django.contrib.auth.hashers import make_password

from .serializers import (
    UserRegistrationSerializer,
    )

from .models import MyUser, TemporaryUser
from .serivces import (
    generate_otp_code,
    check_otp_code
)
from .tasks import (
    send_otp_code
)

class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            if MyUser.objects.filter(email=serializer.validated_data['email']).exists():
                return Response(
                    {'message':'Email already exists'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if TemporaryUser.objects.filter(email=serializer.validated_data['email']).exists():
                TemporaryUser.objects.filter(email=serializer.validated_data['email']).delete()

            with transaction.atomic():
                otp_code = generate_otp_code()
                password = make_password(serializer.validated_data['password'])
                tempUser = TemporaryUser.objects.create(
                    username=serializer.validated_data['username'],
                    email=serializer.validated_data['email'],
                    password=password,
                    user_otp=otp_code,
                    user_otp_created_at=timezone.now()
                )
                transaction.on_commit(lambda: send_otp_code.delay(tempUser.user_otp, tempUser.email))

                return Response(
                    {'message': 'The code was sent to your email, please confirm it to finish registration',
                     'user_id':tempUser.id
                    }, status=status.HTTP_200_OK
                )
            
                
                
        
