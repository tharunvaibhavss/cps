from rest_framework import views, permissions, status
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from apps.bookings.models import PickupRequest
import pandas as pd
import io
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

class DownloadReceiptView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, booking_id):
        booking = get_object_or_404(PickupRequest, id=booking_id)

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        
        # Header
        p.setFont("Helvetica-Bold", 18)
        p.drawString(50, 750, "COURIER PICKUP SCHEDULER")
        p.setFont("Helvetica", 10)
        p.drawString(50, 735, "Official Booking & Pickup Receipt")
        p.line(50, 725, 550, 725)

        # Receipt Body
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, 690, f"Tracking #: {booking.tracking_number}")
        p.setFont("Helvetica", 10)
        p.drawString(50, 670, f"Date: {booking.created_at.strftime('%Y-%m-%d %H:%M')}")
        p.drawString(50, 650, f"Status: {booking.status}")

        p.drawString(50, 620, f"Pickup Contact: {booking.pickup_contact_name} ({booking.pickup_phone})")
        p.drawString(50, 605, f"Pickup Address: {booking.pickup_address[:60]}")
        p.drawString(50, 585, f"Delivery Contact: {booking.delivery_contact_name} ({booking.delivery_phone})")
        p.drawString(50, 570, f"Delivery Address: {booking.delivery_address[:60]}")

        p.line(50, 550, 550, 550)
        p.setFont("Helvetica-Bold", 11)
        p.drawString(50, 530, f"Item: {booking.package_name} [{booking.package_category}]")
        p.drawString(50, 515, f"Weight: {booking.approx_weight_kg} kg | Size: {booking.package_size}")
        p.drawString(50, 500, f"Fragile: {'Yes' if booking.is_fragile else 'No'}")

        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, 460, f"Total Amount Paid: ${booking.estimated_price}")
        p.setFont("Helvetica-Oblique", 9)
        p.drawString(50, 420, "Thank you for using Courier Pickup Scheduler AI Automation.")

        p.showPage()
        p.save()

        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Receipt_{booking.tracking_number}.pdf"'
        return response


class ExportExcelView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        bookings = PickupRequest.objects.all().values(
            'tracking_number', 'status', 'pickup_contact_name',
            'pickup_phone', 'pickup_address', 'delivery_contact_name',
            'delivery_address', 'package_name', 'package_category',
            'approx_weight_kg', 'estimated_price', 'created_at'
        )
        
        df = pd.DataFrame(list(bookings))
        
        # Convert timezone-aware datetimes to formatted strings for Excel compatibility
        if not df.empty and 'created_at' in df.columns:
            df['created_at'] = df['created_at'].astype(str)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Courier Pickups', index=False)
        
        output.seek(0)
        response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Courier_Pickups_Report.xlsx"'
        return response


class ExportPDFView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        bookings = PickupRequest.objects.all().order_by('-created_at')

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        
        # Header
        p.setFont("Helvetica-Bold", 16)
        p.drawString(40, 750, "COURIERFLOW PICKUP SCHEDULER")
        p.setFont("Helvetica", 10)
        p.drawString(40, 735, f"Dispatch & Operational Summary Report - Generated {datetime.date.today()}")
        p.line(40, 725, 570, 725)

        # Summary Metrics Box
        p.setFont("Helvetica-Bold", 11)
        p.drawString(40, 705, f"Total Orders: {bookings.count()}")
        p.drawString(200, 705, f"Completed Deliveries: {bookings.filter(status='DELIVERED').count()}")
        p.drawString(400, 705, f"Active/Assigned: {bookings.filter(status='ASSIGNED').count()}")
        p.line(40, 695, 570, 695)

        # Table Headers
        p.setFont("Helvetica-Bold", 9)
        p.drawString(40, 675, "Tracking #")
        p.drawString(130, 675, "Customer Name")
        p.drawString(240, 675, "Package Details")
        p.drawString(370, 675, "Status")
        p.drawString(470, 675, "Amount ($)")
        p.line(40, 665, 570, 665)

        # Table Rows
        y = 650
        p.setFont("Helvetica", 8.5)

        for b in bookings[:25]:
            p.drawString(40, y, str(b.tracking_number))
            p.drawString(130, y, str(b.pickup_contact_name[:18]))
            p.drawString(240, y, f"{b.package_name[:18]} ({b.approx_weight_kg}kg)")
            p.drawString(370, y, str(b.status))
            p.drawString(470, y, f"${b.estimated_price}")
            y -= 20
            if y < 50:
                p.showPage()
                y = 750

        p.showPage()
        p.save()

        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Courier_Dispatch_Report.pdf"'
        return response
