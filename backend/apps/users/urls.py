from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AddressViewSet, UserManagementViewSet

router = DefaultRouter()
router.register(r'addresses', AddressViewSet, basename='address')
router.register(r'accounts', UserManagementViewSet, basename='user-accounts')

urlpatterns = [
    path('', include(router.urls)),
]
