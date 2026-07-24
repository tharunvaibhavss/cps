from django.urls import path
from .views import AIChatAssistantView, SystemHealthView, SeedDemoDataView

urlpatterns = [
    path('ai-chat/', AIChatAssistantView.as_view(), name='ai-chat'),
    path('health/', SystemHealthView.as_view(), name='health'),
    path('system-health/', SystemHealthView.as_view(), name='system-health'),
    path('seed-demo-data/', SeedDemoDataView.as_view(), name='seed-demo-data'),
]
