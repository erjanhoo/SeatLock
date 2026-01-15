from datetime import timedelta

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from django.db import transaction
from django.utils import timezone
from django.utils import time
from django.contrib.auth.hashers import make_password

from .serializers import (
    UserRegistrationSerializer,
    UserOTPVerificationSerializer,

    UserLoginSerializer
    )

from .models import MyUser, TemporaryUser
from .serivces import (
    generate_otp_code,
    check_otp_code
)
from .tasks import (
    send_otp_code,
    send_email
)

from django.contrib.auth import get_user_model

User = get_user_model()

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
            

class UserRegistrationOTPVerificationView(APIView):
    def post(self, request):
        serializer = UserOTPVerificationSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            temp_reg_id = serializer.validated_data['user_id']
            entered_otp_code = serializer.validated_data['entered_otp_code']

            if not TemporaryUser.objects.filter(id=temp_reg_id):
                return Response(
                    {'message':'Registration intent was not found'},
                    status=status.HTTP_404_NOT_FOUND
                    )
            
            otp_code_expiry = 5
            current_time = timezone.now()
            temp_reg_otp_created_at = temp_reg_id.user_otp_created_at
            temp_reg_user = TemporaryUser.objects.get(id=temp_reg_id)

            if (current_time - temp_reg_otp_created_at).total_seconds() > otp_code_expiry * 60:
                return Response(
                    {'message' : 'Code has expired, request a new one please'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if check_otp_code(entered_otp_code, temp_reg_user.user_otp):
                user = User(
                    username=temp_reg_user.username,
                    email=temp_reg_user.email
                )
                user.set_password(temp_reg_user.password)
                user.save()

                temp_reg_user.delete()

                return Response(
                    {'message' : 'You have successfully registered! '},
                    status=status.HTTP_200_OK
                )
            
            send_email.delay(user.email, f'You have succesffully registered! Welcome {user.username}')

            refresh = RefreshToken.for_user(user=user)

            return Response({
                'refresh' : str(refresh),
                'access' : str(refresh.access_token()),
                'user_id' : user.id,
                'message' : 'Welcome to SeatLock! '
            })




class UserLoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
                      
    
            
                
                
        
