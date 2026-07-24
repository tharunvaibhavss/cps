from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import SavedAddress
from .serializers import SavedAddressSerializer, UserManagementSerializer

User = get_user_model()

class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = SavedAddressSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        user = self.request.user
        if user and user.is_authenticated:
            return SavedAddress.objects.filter(user=user).order_by('-is_default', '-created_at')
        return SavedAddress.objects.all().order_by('-is_default', '-created_at')

    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        address = self.get_object()
        user = request.user if request.user and request.user.is_authenticated else address.user
        SavedAddress.objects.filter(user=user).update(is_default=False)
        address.is_default = True
        address.save()
        return Response({'message': f'"{address.title}" set as default address.'})

class UserManagementViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-created_at')
    serializer_class = UserManagementSerializer
    permission_classes = [permissions.AllowAny]
