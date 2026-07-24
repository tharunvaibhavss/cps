from rest_framework import status, views, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from .serializers import (
    RegisterSerializer, UserSerializer, VerifyOTPSerializer,
    ForgotPasswordSerializer, ResetPasswordSerializer
)
from .models import OTPCode, PasswordResetToken
import random
import uuid

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate OTP
        otp_val = str(random.randint(100000, 999999))
        OTPCode.objects.create(user=user, code=otp_val)

        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'otp_preview': otp_val, # Provided for local testing demo
            'message': 'User registered successfully. OTP sent for verification.'
        }, status=status.HTTP_201_CREATED)

class LoginView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Please provide email and password'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(email=email, password=password)
        if not user:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

class VerifyOTPView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        code = serializer.validated_data['otp']

        try:
            user = User.objects.get(email=email)
            otp_obj = OTPCode.objects.filter(user=user, code=code, is_used=False).order_by('-created_at').first()

            if otp_obj and otp_obj.is_valid():
                otp_obj.is_used = True
                otp_obj.save()
                user.is_verified = True
                user.save()
                return Response({'message': 'Email verified successfully!'}, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid or expired OTP code'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

class ForgotPasswordView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
            token = str(uuid.uuid4())
            PasswordResetToken.objects.create(user=user, token=token)
            return Response({
                'message': 'Password reset token generated.',
                'reset_token': token # Included for instant demonstration
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'message': 'If user exists, a reset link will be sent.'}, status=status.HTTP_200_OK)

class ResetPasswordView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']

        token_obj = PasswordResetToken.objects.filter(token=token, is_used=False).first()
        if not token_obj:
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)

        user = token_obj.user
        user.set_password(new_password)
        user.save()
        token_obj.is_used = True
        token_obj.save()

        return Response({'message': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
