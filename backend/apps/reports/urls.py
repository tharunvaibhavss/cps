from django.urls import path
from .views import DownloadReceiptView, ExportExcelView, ExportPDFView

urlpatterns = [
    path('receipt/<uuid:booking_id>/', DownloadReceiptView.as_view(), name='download-receipt'),
    path('export-excel/', ExportExcelView.as_view(), name='export-excel'),
    path('export-pdf/', ExportPDFView.as_view(), name='export-pdf'),
]
