from django.db import models
from datetime import date
# Create your models here.
from datetime import datetime, timedelta
from django.utils import timezone
import uuid
from django.db import transaction

class OTP(models.Model):
    email = models.EmailField(null=True, blank=True)
    otp = models.CharField(max_length=5)
    created_at = models.DateTimeField(auto_now_add=True)
    attempts = models.IntegerField(default=0)  # Track attempts

    def __str__(self):
        return f'OTP for {self.email}: {self.otp}'
	
    def save(self, *args, **kwargs):
        with transaction.atomic():
            # Delete existing OTPs for the same email
            OTP.objects.filter(email=self.email).delete()
            super().save(*args, **kwargs)

class CustomeUser(models.Model):
	username = models.CharField(max_length=100, blank=True, null=True)
	email = models.EmailField(null=True, blank=True)
	phone_number = models.CharField(max_length=11, null=True, blank=True)
	def __str__(self):
		return self.username


class BedType(models.Model):
    bed_type = models.CharField(max_length=300, null=True)
    def __str__(self):
        return self.bed_type
    
class RoomSize(models.Model):
    size = models.IntegerField(null=True, blank=True)
    def __str__(self):
        return str(self.size)  # Convert the integer to a string

class DisplaySlider(models.Model):
    name = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True,null=True)
    slider_image  = models.ImageField(upload_to="Slider", default='0.jpeg')
    button_name = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.name

class FeatureList(models.Model):
    feature_name = models.CharField(max_length=200, null=True)
    feature_images = models.ImageField(upload_to="Feature", default='0.jpeg')  # Removed unnecessary height/width fields

    def __str__(self):
        return self.feature_name
    
class Room(models.Model):
    room_no = models.CharField(max_length=5, null=True)
    bed_type = models.CharField(max_length=100, null=True)
    room_type = models.CharField(max_length=200, null=True)
    room_description = models.TextField(null=True, blank=True)
    size = models.CharField(max_length=20, null=True)
    is_available = models.BooleanField(default=True)
    price = models.FloatField()
    quantity = models.IntegerField(null=True, blank=True)
    room_people = models.CharField(max_length=5, null=True, blank=True)
    features = models.ManyToManyField(FeatureList)
    
    # New fields for hold functionality

    def __str__(self):
        return f"Room No: {self.room_no}"

   
    
class Images(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True, related_name='images')  # Added related_name for reverse lookup
    room_image = models.ImageField(upload_to="media", default='0.jpeg')  # Removed `height_field` and `width_field`

    def __str__(self):
        return f"Image for Room {self.room.room_no}"


class PreBooking(models.Model):
    prebrookingId = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    room_id = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True)
    room_quantity = models.IntegerField(null=True, blank=True)
    adults = models.IntegerField(null=True, blank=True)
    check_in_date = models.DateField(null=True, blank=True)
    check_out_date = models.DateField(null=True, blank=True)
    start_time = models.DateTimeField(auto_now_add=True)  # Store the time when booking is created
    expiration_time = models.DateTimeField()
    is_on_hold = models.BooleanField(default=False)
    hold_until = models.DateTimeField(null=True, blank=True)  # Store hold expiration time

    def save(self, *args, **kwargs):
        if not self.pk:  # Only set it if it's a new instance
            self.expiration_time = timezone.now() + timezone.timedelta(minutes=15)  # 10 minutes countdown
        super().save(*args, **kwargs)

    @property
    def remaining_time(self):
        return self.expiration_time - timezone.now()  # Calculate remaining time

    def hold_room(self):
        self.is_on_hold = True
        self.hold_until = timezone.now() + timedelta(minutes=1)  # Extend hold time as needed
        self.save()

    def release_hold(self):
        self.is_on_hold = False
        self.hold_until = None
        self.save()

    def is_hold_expired(self):
        if self.hold_until and timezone.now() > self.hold_until:
            self.release_hold()
            return True
        return False

    def __str__(self):
        return f"PreBooking {self.prebrookingId} for  {self.room_id}"




class Reservation(models.Model):
    confirmation_number = models.CharField(max_length=10, unique=True, blank=True, null=True)  # Add this field
    room_no = models.ForeignKey(Room, on_delete=models.CASCADE)
    name=models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    email=models.CharField(max_length=100)
    address = models.TextField(null=True, blank=True)
    check_in_date = models.DateField(auto_now=False, auto_now_add=False)
    check_out_date = models.DateField(auto_now=False, auto_now_add=False)
    amount = models.FloatField()
    booked_on = models.DateTimeField(auto_now_add=True) 
    special_request = models.TextField(null=True, blank= True)
    arrival_time = models.CharField(max_length=200, null=True)
    room_quantity = models.IntegerField(null=True, blank=True)
    adults = models.IntegerField(null=True, blank=True)
    payment = models.BooleanField(default=False)
    is_check_in = models.BooleanField(default=False)
    is_check_out = models.BooleanField(default=False)
    def __str__(self):
        return "Booking ID: "+str(self.id)

    @property
    def is_past_due(self):
        return date.today() >self.end_day

class Contact(models.Model):
    name=models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    email=models.CharField(max_length=100)
    message=models.TextField(max_length=2000)
    def __str__(self):
        return self.name
    
class ReferenceObject(models.Model):
    name = models.CharField(max_length=100,null=True,blank=True)
    width_cm = models.FloatField(null=True,blank=True)  # Known width in cm

class Measurement(models.Model):
    image = models.ImageField(upload_to='images/')
    length = models.FloatField(null=True, blank=True)