from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VerifyQRView, ProofOfPickupViewSet, RouteOptimizationView

router = DefaultRouter()
router.register(r'proof', ProofOfPickupViewSet, basename='proof')

urlpatterns = [
    path('verify-qr/', VerifyQRView.as_view(), name='verify-qr'),
    path('optimize-route/', RouteOptimizationView.as_view(), name='optimize-route'),
    path('', include(router.urls)),
]
