from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
)
from .models import AccessToken, Role, UserRole
from .authentication import TokenAuthentication
from .permissions import AccessRulePermission

User = get_user_model()


def _build_username(last_name, first_name, patronymic):
    result = []
    for value in (last_name, first_name, patronymic):
        if value:
            result.append(value)
    return " ".join(result).strip()


class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        if User.objects.filter(email=email).exists():
            return Response({'message': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        username = _build_username(
            serializer.validated_data['last_name'],
            serializer.validated_data['first_name'],
            serializer.validated_data.get('patronymic'),
        )

        user = User.objects.create_user(
            username=username or email,
            email=email,
            password=serializer.validated_data['password'],
            last_name=serializer.validated_data['last_name'],
            first_name=serializer.validated_data['first_name'],
            patronymic=serializer.validated_data.get('patronymic', ''),
        )

        try:
            default_role = Role.objects.get(code='user')
            UserRole.objects.get_or_create(user=user, role=default_role)
        except Role.DoesNotExist:
            pass

        return Response(
            {'message': 'User registered', 'user_id': user.id},
            status=status.HTTP_201_CREATED,
        )


class UserLoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = User.objects.get(email=serializer.validated_data['email'])
        except User.DoesNotExist:
            return Response({'message': 'Invalid email or password'}, status=status.HTTP_400_BAD_REQUEST)

        if not user.is_active or not user.check_password(serializer.validated_data['password']):
            return Response({'message': 'Invalid email or password'}, status=status.HTTP_400_BAD_REQUEST)

        token = AccessToken.create_for_user(user)
        return Response(
            {
                'access_token': token.key,
                'expires_at': token.expires_at,
                'token_type': 'Token',
            },
            status=status.HTTP_200_OK,
        )


class UserLogoutView(APIView):
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        token = request.auth
        if isinstance(token, AccessToken):
            token.revoke()
        return Response({'message': 'Logged out'}, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [AccessRulePermission]
    access_resource = 'profile'

    def get(self, request):
        serializer = UserProfileSerializer(instance=request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        serializer = UserProfileSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        if 'email' in serializer.validated_data:
            if User.objects.filter(email=serializer.validated_data['email']).exclude(id=request.user.id).exists():
                return Response({'message': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
            request.user.email = serializer.validated_data['email']

        if any(k in serializer.validated_data for k in ('last_name', 'first_name', 'patronymic')):
            request.user.last_name = serializer.validated_data.get('last_name', request.user.last_name)
            request.user.first_name = serializer.validated_data.get('first_name', request.user.first_name)
            request.user.patronymic = serializer.validated_data.get('patronymic', request.user.patronymic)
            request.user.username = _build_username(
                request.user.last_name,
                request.user.first_name,
                request.user.patronymic,
            ) or request.user.username

        request.user.save()
        return Response(UserProfileSerializer(instance=request.user).data, status=status.HTTP_200_OK)

    def delete(self, request):
        request.user.is_active = False
        request.user.save(update_fields=['is_active'])

        for token in request.user.access_tokens.filter(revoked_at__isnull=True):
            token.revoke()

        return Response({'message': 'Account deactivated'}, status=status.HTTP_200_OK)


class AdminPanelView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [AccessRulePermission]
    access_resource = 'admin_panel'
    access_action = 'read'

    def get(self, request):
        return Response(
            {
                'message': 'If you see this, you are allowed here.',
                'your_email': request.user.email,
            },
            status=status.HTTP_200_OK,
        )
