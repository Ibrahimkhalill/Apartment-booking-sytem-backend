from rest_framework import serializers
from .models import *

# Serializer for the FeatureList model

class BedTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BedType
        fields = ['id', 'bed_type']

class RoomSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomSize
        fields = ['id', 'size']

class FeatureListSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeatureList
        fields = ['id', 'feature_name', 'feature_images']

# Serializer for the Images model
class ImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Images
        fields = ['id', 'room', 'room_image']

class DisplaySliderSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisplaySlider
        fields = ['id', 'name', 'description',"slider_image","button_name"]


# Serializer for the Room model
class RoomSerializer(serializers.ModelSerializer):
    features = FeatureListSerializer(many=True)  # Serializing many-to-many relation
    images = ImagesSerializer(many=True, read_only=True)  # Serializing one-to-many relation with images
    
    class Meta:
        model = Room
        fields = [
            'id', 
            'room_no', 
            'room_type', 
            'bed_type',
            'size',
            'room_description',
            'is_available', 
            'price', 
            'quantity', 
            'room_people', 
            'features', 
            'images'
            
        ]
        
class PrebookingSerializer(serializers.ModelSerializer):
    room_id = RoomSerializer()  # Serialize the room details
    class Meta:
        model = PreBooking
        fields = ['id', 'room_id', 'room_quantity',
            'adults','check_in_date', 'check_out_date']


# Serializer for the Reservation model
class ReservationSerializer(serializers.ModelSerializer):
    room_no = RoomSerializer()  # Serialize the room details
    
    class Meta:
        model = Reservation
        fields = [
            'id', 
            "confirmation_number",
            'room_no', 
            'name', 
            'phone_number', 
            'email', 
            'address',
            'check_in_date', 
            'check_out_date', 
            'amount', 
            'booked_on',
            'special_request',
            'arrival_time',
            'room_quantity',
            'adults',
            'payment',
            'is_check_in',
            'is_check_out'
        ]

# Serializer for the Contact model
class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'name', 'phone_number', 'email', 'message']


class MeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Measurement
        fields = '__all__'

class ReferenceObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferenceObject
        fields = '__all__'