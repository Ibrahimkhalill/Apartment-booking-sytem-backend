from celery import shared_task
from mainapp.models import PreBooking
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)
HOLD_DURATION = 1  # Duration in minutes

@shared_task
def release_expired_bookings():
    expiration_time = timezone.now() - timedelta(minutes=HOLD_DURATION)
    expired_bookings = PreBooking.objects.filter(is_on_hold=True)
    
    for booking in expired_bookings:
        try:
            booking.release_hold()  # Make sure this method is defined in your PreBooking model
            print(f"Booking {booking.id} released due to timeout.")
        except Exception as e:
            logger.error(f"Error releasing booking {booking.id}: {str(e)}")