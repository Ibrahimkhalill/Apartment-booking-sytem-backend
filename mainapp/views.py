from django.shortcuts import render, redirect
from mainapp.models import *
from email.mime.image import MIMEImage
import os
import random
import string
from django.contrib import messages
from django.http import JsonResponse 
from django.contrib.auth.models import User
# from .tokens import account_activation_token  
from django.db.models import Sum, Q
from rest_framework import status
import logging
import json
logger = logging.getLogger(__name__)
from django.core.mail import EmailMultiAlternatives

from django.template.loader import render_to_string 
from django.core.mail import EmailMessage   
from django.contrib.auth import login as Login_process ,logout,authenticate, get_user_model
from .serializers import *
from django.http import HttpResponse, JsonResponse
from mainapp.models import *
from rest_framework.authtoken.models import Token
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Room, PreBooking,FeatureList  # Adjust the import based on your project structure
# from .utils import measure_foot
from.OtpGenarator import generate_otp
import requests

from django.conf import settings

def index(request):
    return render(request, 'index.html')


@api_view(["POST"])
def send_otp(request):
    if request.method == 'POST':
        email = request.data.get('email')

        try:
            # Generate OTP
            otp = generate_otp()
            # Save OTP to database
            OTP.objects.create(email=email, otp=otp)
            
            # Render the HTML template
            html_content = render_to_string('otp_email_template.html', {'otp': otp, 'email':email})
            
            
            # Send email
            msg = EmailMultiAlternatives(
                subject='Your OTP Code',
                body='This is an OTP email.',
                from_email='hijabpoint374@gmail.com',  # Sender's email address
                to=[email],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send(fail_silently=False)  
            
            return JsonResponse({'message': 'OTP sent to your email.'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'message': 'Invalid method.'})


@api_view(["POST"])
def verify_otp(request):
    if request.method == 'POST':
        otp = request.data.get('otp')

        try:
                otp_record = OTP.objects.get(otp=otp)
                otp_record.attempts += 1  
                otp_record.save()  
                if (timezone.now() - otp_record.created_at).seconds > 120:
                    otp_record.delete()  
                    return Response({'message': ' Otp Expired'})
                else:
                    otp_record.delete()  
                    return Response('success', status=status.HTTP_200_OK)
        except OTP.DoesNotExist:
                return Response({'message': 'Invalid Otp'}, status=status.HTTP_400_BAD_REQUEST)
           
    return Response("Method is not allowed")

@api_view(['POST'])
def signup_view(request):
    if request.method == 'POST':
        
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        phone_number = request.data.get('phone_number')

        existing_user = User.objects.filter(email=email).first()
        if existing_user:
           
            return Response({'message': 'User with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            #
            user = User.objects.create_user(username=username, email=email, password=password)
            customeruser = CustomeUser(username=username, email=email, phone_number = phone_number)
            customeruser.save()

            if user:
                return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'message': 'User registration failed'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'message': 'User registration failed', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
def login_view(request):
    if request.method == 'POST':
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            user = get_object_or_404(CustomeUser, email=email)

            # Authenticate user using email and password
            user_auth = authenticate(request, username=user.username, password=password)

            if user_auth is not None:
                django_login(request, user_auth)
                token, created = Token.objects.get_or_create(user=user_auth)
                
                # Set the token as an HttpOnly cookie
                response = JsonResponse({'message': 'Login successful', 'username': user.username,'email':user.email, "token": token.key}, status=status.HTTP_200_OK)
                response.set_cookie(
                    'authToken', 
                    token.key, 
                    httponly=True, 
                    secure=False, 
                    samesite='None',
                    max_age=60*60*24*30, # Cookie will last for 30 days
                    expires=None,
                    path= "/"
                )
                print("Set-Cookie:", response.cookies)
                # Return CSRF token if needed
                response['X-CSRFToken'] = get_token(request)
                
                return response
            else:
                return JsonResponse({'error': 'Invalid credentials'}, status=401)

        except CustomeUser.DoesNotExist:
            return JsonResponse({'error': 'User does not exist'}, status=404)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated]) 
@api_view(['GET'])
def check_auth(request):
 
    print("User is authenticated:", request.user.is_authenticated)
    if request.user.is_authenticated:
        return Response({'username': request.user.username, 'email': request.user.email}, status=200)
    else:
        return Response({'error': 'Not authenticated'}, status=401)



@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated]) 
def logout_api_view(request):
    # User ke logout korar process
    request.user.auth_token.delete()  # Token delete kore deya
    return JsonResponse({"message": "Logout successful"}, status=200)



@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated]) 
def password_change(request):
    old_password = request.data.get('oldPassword')
    new_password = request.data.get('newPassword')

    # Authenticate the user with the old password
    user = authenticate(username=request.user.username, password=old_password)

    if user is not None:
        # If the old password matches, set the new password
        user.set_password(new_password)
        user.save()

        return JsonResponse({"message": "Password changed successfully"}, status=200)
    else:
        # If old password is incorrect
        return JsonResponse({"message": "Old password did not match"}, status=status.HTTP_400_BAD_REQUEST)
    
    


@api_view(['POST'])
def book_room(request):
    # Log the request data for debugging
    logger.info(f"Request data: {request.data}")

    # Get room booking data from request
    room_id = request.data.get("room")
    room_quantity = request.data.get('room_quantity')
    adults = request.data.get('adults')
    check_in = request.data.get('check_in')
    check_out = request.data.get('check_out')

    # Check if required fields are present
    if not room_id or not check_in or not check_out:
        return Response({"error": "Missing required fields."}, status=400)

    # Fetch the Room object based on the room_id
    room = get_object_or_404(Room, id=room_id)

    # Check for overlapping pre-bookings or holds
    overlapping_bookings = PreBooking.objects.filter(
        room_id=room,
        check_in_date__lt=check_out,  # Check if check-in date is before the new check-out
        check_out_date__gt=check_in,   # Check if check-out date is after the new check-in
        is_on_hold=True,                # Ensure the room is on hold
        expiration_time__gt=timezone.now()  # Ensure the hold time has not expired
    )

    if overlapping_bookings.exists():
        return Response({"error": "Room is already booked or on hold for the selected dates."}, status=status.HTTP_226_IM_USED)

    # Delete expired bookings (where expiration time has passed)
    expired_bookings = PreBooking.objects.filter(
        expiration_time__lt=timezone.now()
    )
    expired_count = expired_bookings.count()
    expired_bookings.delete()  # Delete expired bookings

    # Create a new PreBooking object (UUID will be automatically generated by the model)
    booking = PreBooking(
        room_id=room,
        room_quantity=room_quantity,
        adults=adults,
        check_in_date=check_in,
        check_out_date=check_out,
        
    )
    
    booking.save() 
    # Check if the room is available and not currently on hold
    if not booking.is_on_hold:
        booking.hold_room()  # Custom method to hold the room (update room status to "on hold")
        return Response({
            "message": "Room has been put on hold for 15 minutes.",
            "uuid": str(booking.prebrookingId),  # Access the auto-generated UUID
            "expiration_time": booking.expiration_time.isoformat(),
            "expired_count": expired_count,  # Return the count of deleted expired bookings
        }, status=200)
    else:
        return Response({"error": "Room is not available or already on hold."}, status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET'])
def get_booking(request, uuid):
    # Fetch the booking object or return a 404 if it doesn't exist
    booking = get_object_or_404(PreBooking, prebrookingId=uuid)
    booking_serializer = PrebookingSerializer(booking)

    # Get remaining time in seconds
    remaining_time = booking.remaining_time.total_seconds()

    # Check if the session has expired
    if remaining_time <= 0:
        return Response({ 'message': "Session expired. Please make a new booking.", }, status=status.HTTP_205_RESET_CONTENT)  # You can choose an appropriate status code

    return Response({
        'uuid': str(booking.prebrookingId),
        'remaining_time': max(0, remaining_time),  # Ensure it's not negative
        'booking': booking_serializer.data
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
def release_room(request, uuid):
   
    prebooking = get_object_or_404(PreBooking,prebrookingId=uuid, is_on_hold =True)

    # Release hold if it's expired or manually triggered
    if prebooking.is_on_hold:
        prebooking.release_hold()
        return Response({'status': 'success', 'message': 'For security reasons after 15 minutes of inactivity your session expires.'}, status=200)
    else:
        return Response({'error': 'Room is not currently on hold.'}, status=400)
    
def contact(request):
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        phone_number = request.POST['phone_number']
        message = request.POST['messages']
        data = Contact(name=name, email=email,
                       phone_number=phone_number, message=message)
        data.save()
        messages.success(request, "Your Message Send Successfully")
        return redirect('/contact/')
    else:
        return render(request, "mainapp/contact.html")

@api_view(["GET"])
def get_room(request):
    rooms = Room.objects.all()
    room_serializer = RoomSerializer(rooms, many=True)
    # Debugging output
  
    return Response(room_serializer.data, status=status.HTTP_200_OK)

@api_view(["GET"])
def get_feature_list(request):
    fetaures = FeatureList.objects.all()
    feature_serializer = FeatureListSerializer(fetaures, many=True)
    # Debugging output
  
    return Response(feature_serializer.data, status=status.HTTP_200_OK)

def confirmation(request):
    room = Room.objects.get(pk=13) 
    images = Images.objects.filter(room=room)[0]
   
   
    context = {
        "image" :images,
        "room": room
    }

    return render(request,"confirmation_email.html",context)

def generate_confirmation_number():
    while True:
        confirmation_number = 'Ai' + ''.join(random.choices(string.digits, k=4))  # e.g., VJ0069
        # Check if the confirmation number already exists
        if not Reservation.objects.filter(confirmation_number=confirmation_number).exists():
            return confirmation_number


@api_view(['POST'])
def reservation(request, room_id):
    try:
        room = Room.objects.get(pk=room_id)
    except Room.DoesNotExist:
        return Response({"error": "Room not found."}, status=status.HTTP_404_NOT_FOUND)

    # Extract reservation data from the request
    name = request.data.get('name')
    phone_number = request.data.get('phone_number')
    email = request.data.get('email')
    check_in = request.data.get('check_in')
    check_out = request.data.get('check_out')
    amount = request.data.get('amount')
    address = request.data.get('address')
    special_request = request.data.get('special_request')
    room_quantity = request.data.get('room_quantity')
    adults = request.data.get('adults')
    arrival_time = request.data.get('arrival_time')
    confirmation_number = generate_confirmation_number()

    # Create reservation instance
    reservation_data = Reservation(
        confirmation_number=confirmation_number,
        room_no=room,
        name=name,
        phone_number=phone_number,
        email=email,
        check_in_date=check_in,
        check_out_date=check_out,
        amount=amount,
        address=address,
        special_request=special_request,
        room_quantity=room_quantity,
        adults=adults,
        arrival_time=arrival_time
    )
    reservation_data.save()

    # Attempt to retrieve PreBooking
    try:
        prebooking = PreBooking.objects.get(
            check_in_date=check_in,
            check_out_date=check_out,
            is_on_hold=True,
            room_id=room
        )
        prebooking.delete()  # Release the hold if it exists
    except PreBooking.DoesNotExist:
        pass  # No need to release if no prebooking exists

    # Mark room as unavailable after reservation
    room.is_available = False
    room.save()

    # Handle image attachment for confirmation email
    images = Images.objects.filter(room=room).first() 
    image_path = images.room_image.path if images else None

    # Prepare confirmation email
    mail_subject = 'Booking Confirmation Email'  
    message = render_to_string('confirmation_email.html', {  
        'user': name,  
        'phone_number': phone_number,  
        'email': email,  
        'check_in': check_in,  
        'check_out': check_out,
        'amount': amount,
        'adults': adults,
        'room': room,
        'confirmation_number':confirmation_number,
        'image_url': 'cid:room_image'
    })  
    
    to_email = email
    email_message = EmailMessage(mail_subject, message, to=[to_email]) 
    email_message.content_subtype = "html"
    
    # Attach image if available
    if image_path:
        with open(image_path, 'rb') as img_file:
            img = MIMEImage(img_file.read())
            img.add_header('Content-ID', '<room_image>')
            img.add_header('Content-Disposition', 'inline', filename=os.path.basename(image_path))
            email_message.attach(img)
    
    email_message.send()  

    return Response({
    "message": "Reservation successful.",
    "confirmation_number": reservation_data.confirmation_number  # Assuming confirmation_number is saved in reservation_data
}, status=status.HTTP_201_CREATED)



def get_date(request):
    if request.method == "POST":

        room_id = request.POST['room_no']
        room = Room.objects.filter(room_no = room_id)[0]
        check_in = request.POST['check_in']
        check_out = request.POST['check_out']
        
        # print(bill)
        date = Reservation.objects.filter(
            room_no=room, check_in_date=check_in, check_out_date=check_out)
        date = date.count()
        print(date)
        # list= []
        # list.append(
        #     bill,
        #     date
        # )
        return JsonResponse(date, safe=False)


@api_view(["POST"])
def available_room(request):
    check_in_date = request.data.get('checkInDate')
    check_out_date = request.data.get('checkOutDate')
    room_quantity = request.data.get('room_quantity')

    if not check_in_date or not check_out_date:
        return Response(
            {"error": "Both checkInDate and checkOutDate are required."}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Validate room_quantity
        room_quantity = int(room_quantity)  # Convert to integer
    except (ValueError, TypeError):
        logger.error("Invalid room_quantity: %s", room_quantity)
        return Response(
            {"error": "room_quantity must be an integer."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Step 1: Find rooms that are already booked within the date range
        conflicting_reservations = Reservation.objects.filter(
            Q(check_in_date__lte=check_out_date) & 
            Q(check_out_date__gte=check_in_date)
        )

        # Step 2: Get room numbers of conflicting reservations
        booked_room_ids = [res.room_no.id for res in conflicting_reservations]

        # Step 3: Calculate total quantity already booked for each room
        room_bookings = Reservation.objects.filter(
            Q(check_in_date__lte=check_out_date) & 
            Q(check_out_date__gte=check_in_date)
        ).values('room_no').annotate(total_booked=Sum('room_quantity'))

        available_rooms = []
        room_availabilities = {}

        # Step 4: Check availability for booked rooms and calculate remaining quantity
        for booking in room_bookings:
            room = Room.objects.get(id=booking['room_no'])
            total_booked = booking['total_booked']
            
            available_quantity = room.quantity - total_booked  # Subtract booked quantity from total room quantity
            
            if available_quantity >= room_quantity:
                available_rooms.append(room)
                room_availabilities[room.id] = available_quantity  # Store available quantity for each room

        # Step 5: Find rooms that are not booked at all within the date range
        unbooked_rooms = Room.objects.exclude(id__in=booked_room_ids).filter(quantity__gte=room_quantity)
        
        # Step 6: Add unbooked rooms to the available rooms list
        for room in unbooked_rooms:
            available_rooms.append(room)
            room_availabilities[room.id] = room.quantity  # Full quantity available since no booking

        # Step 7: If no rooms are available, return a message
        if not available_rooms:
            return Response(
                {"error": "No rooms are available with the requested quantity for the selected dates."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Step 8: Serialize available rooms and attach available quantity
        available_rooms_data = []
        for room in available_rooms:
            room_data = RoomSerializer(room).data
            room_data['available_quantity'] = room_availabilities.get(room.id, 0)  # Attach available quantity
            available_rooms_data.append(room_data)

        logger.info("Available rooms serialized with available quantities: %s", available_rooms_data)
        return Response(available_rooms_data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception("Error processing available_room request: %s", str(e))
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

  

@api_view(["POST"])
def available_room_by_id(request, room_id):
    check_in_date = request.data.get('checkInDate')
    check_out_date = request.data.get('checkOutDate')
    room_quantity = request.data.get('room_quantity')

    # Validate required fields
    if not check_in_date or not check_out_date or not room_id:
        return Response(
            {"error": "room_id, checkInDate, and checkOutDate are required."}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Validate room_quantity
        room_quantity = int(room_quantity)  # Convert to integer
    except (ValueError, TypeError):
        logger.error("Invalid room_quantity: %s", room_quantity)
        return Response(
            {"error": "room_quantity must be an integer."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Check if the room with the given room_id exists
        room = Room.objects.filter(id=room_id).first()
        if not room:
            return Response(
                {"error": "Room with the specified room_id not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Find conflicting reservations for the given room and date range
        conflicting_reservations = Reservation.objects.filter(
            Q(check_in_date__lte=check_out_date) & 
            Q(check_out_date__gte=check_in_date) & 
            Q(room_no=room)
        )

        # If there are conflicting reservations, calculate the total booked quantity
        if conflicting_reservations.exists():
            total_booked_quantity = conflicting_reservations.aggregate(
                total_booked=Sum('room_quantity')
            )['total_booked'] or 0  # If no bookings, return 0
        else:
            # If no bookings exist, set the booked quantity to 0
            total_booked_quantity = 0

        # Available quantity is total quantity minus already booked quantity
        available_quantity = room.quantity - total_booked_quantity
        print("room.quantity",room.quantity , available_quantity)

        # Check if the available quantity is enough to accommodate the requested quantity
        if available_quantity < room_quantity:
             return Response(
              {"error": "The requested number of rooms is not available for the selected dates. We have {} room(s) available, but you requested {} room(s).".format(
            available_quantity, room_quantity)},
        status=status.HTTP_400_BAD_REQUEST
    )

        # If available, serialize the room
        available_serialize = RoomSerializer(room)
        logger.info("Room is available with remaining quantity: %s", available_serialize.data)
        return Response(available_serialize.data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception("Error processing available_room request: %s", str(e))
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
def get_reservation(request):    
    # Filter reservations that start from now into the past and order by date descending
    reservations = Reservation.objects.all().order_by('-booked_on')
    # Serialize the filtered reservations
    reservation_serializer = ReservationSerializer(reservations, many=True)
    
    # Return the serialized data
    return Response(reservation_serializer.data, status=status.HTTP_200_OK)


@api_view(["PUT"])
def update_reservation(request, id):
    # Retrieve the booking, or return a 404 error if not found
    booking = get_object_or_404(Reservation, id=id)
    
    # Get the 'is_check_in' and 'is_check_out' values from the request data
    is_check_in = request.data.get('is_check_in')
    is_check_out = request.data.get('is_check_out')
    
    updated = False
    
    # Update the 'is_check_in' field if provided
    if is_check_in is not None:
        booking.is_check_in = is_check_in
        updated = True
    
    # Update the 'is_check_out' field if provided
    if is_check_out is not None:
        booking.is_check_out = is_check_out
        updated = True
    
    # Save the booking if any field was updated
    if updated:
        booking.save()
        return Response({"message": "Update Successfully"}, status=status.HTTP_200_OK)
    
    # If neither 'is_check_in' nor 'is_check_out' is provided
    return Response({"error": "Either is_check_in or is_check_out field is required"}, status=status.HTTP_400_BAD_REQUEST)

# save room
@api_view(["POST"])
def add_room(request):
    if request.method == 'POST':
        # Extract form fields
        room_no = request.POST.get('roomNo')
        room_name = request.POST.get('roomName')
        bed_type = request.POST.get('bedType')
        size = request.POST.get('size')
        max_people = request.POST.get('maxPeople')
        quantity = request.POST.get('quantity')
        price = request.POST.get('price')
        room_address = request.POST.get('room_address')
        description = request.POST.get('description')

        # Extract features (JSON string to list)
        feature_ids = json.loads(request.POST.get('features', '[]'))

        # Create and save the room object
        room = Room(
            room_no=room_no, 
            room_type=room_name, 
            bed_type=bed_type, 
            size=size, 
            room_people=max_people, 
            price=price, 
            room_address=room_address,
            quantity=quantity, 
            room_description=description
        )
        room.save()

        # Add the features to the room
        for feature_id in feature_ids:
            try:
                feature = FeatureList.objects.get(id=feature_id)  # Get the feature by ID
                room.features.add(feature)  # Add the feature to the room's many-to-many field
            except feature.DoesNotExist:
                print(f"Feature with ID {feature_id} does not exist")

        # Save the images
        images = request.FILES.getlist('images')
        print("images",images)
        for image in images:
            print(image,room)
            image_data = Images(room=room, room_image=image)
            image_data.save()

        return JsonResponse({'message': 'Room created successfully!'})
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)



@api_view(["GET"])
def get_room_by_id(request,id):
    rooms = get_object_or_404(Room, id =id )
    room_serializer = RoomSerializer(rooms)
    # Debugging output
  
    return Response(room_serializer.data, status=status.HTTP_200_OK)

@api_view(["PUT"])
def updated_room(request,id):
    if request.method == 'PUT':
        # Extract form fields
        room_no = request.POST.get('roomNo')
        room_name = request.POST.get('roomName')
        bed_type = request.POST.get('bedType')
        size = request.POST.get('size')
        max_people = request.POST.get('maxPeople')
        quantity = request.POST.get('quantity')
        price = request.POST.get('price')
        room_address = request.POST.get('room_address')
        description = request.POST.get('description')

        # Extract features (JSON string to list)
        feature_ids = json.loads(request.POST.get('features', '[]'))

        room = get_object_or_404(Room, id=id)
        print("price",price)
        # Create and save the room object
       
        room.room_no=room_no
        room.room_type=room_name
        room.bed_type=bed_type
        room.size=size
        room.room_people=max_people
        room.price=price
        room.quantity=quantity
        room.room_description=description
        room.room_address = room_address
    
        room.save()
        room.features.clear()

        # Add the features to the room
        for feature_id in feature_ids:
            try:
                feature = FeatureList.objects.get(id=feature_id)  # Get the feature by ID
                room.features.add(feature)  # Add the feature to the room's many-to-many field
            except feature.DoesNotExist:
                print(f"Feature with ID {feature_id} does not exist")

        # Save the images
        images_update = request.FILES.getlist('images_to_update')  # Use request.FILES for image files
        images_add = request.FILES.getlist('images_to_add')        # Images to be added
        image_ids = request.POST.getlist('image_ids')  

        if images_update or images_add :
        
            print("Images to update:", images_update)
            print("Images to add:", images_add)
            print("Image IDs:", image_ids)

            # Update existing images
            for i, image_id in enumerate(image_ids):
                try:
                    existing_image = Images.objects.get(id=image_id)  # Find the existing image by ID
                    if existing_image:
                        existing_image.room_image = images_update[i]  # Update the existing image
                        existing_image.save()
                except Images.DoesNotExist:
                    print(f"Image with ID {image_id} does not exist.")
            
            # Add new images
            for image_add in images_add:
                room_image = Images(room=room, room_image=image_add)  # Assuming `room` is defined
                room_image.save()
            return JsonResponse({'message': 'Room updated successfully!'})
        
        else: 
            return JsonResponse({'message': 'Room updated successfully!'})
        
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)


@api_view(["DELETE"])
def detele_Room(request, id):
 
    room = get_object_or_404(Room, id = id)
    room.delete()
    return Response({'message': 'Room Deleted successfully!'}, status=status.HTTP_200_OK)

@api_view(["DELETE"])
def delete_feature_from_room(request, room_id, feature_id):
    # Get the Room object
    room = get_object_or_404(Room, id=room_id)
    
    # Get the FeatureList object
    feature = get_object_or_404(FeatureList, id=feature_id)
    
    # Check if the feature is associated with the room
    if feature in room.features.all():
        # Remove the feature from the specific room
        room.features.remove(feature)
        return Response({'message': 'Feature removed from the room successfully!'}, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Feature not found in this room!'}, status=status.HTTP_404_NOT_FOUND)

@api_view(["DELETE"])
def delete_image_from_room(request,image_id):
    # Get the Room object
    # Get the FeatureList object
    image = get_object_or_404(Images, id=image_id)
    image.delete()
    # Check if the feature is associated with the room
   
    return Response({'message': 'Image delete from the room successfully!'}, status=status.HTTP_200_OK)
    

@api_view(['POST'])
def get_available_rooms(request):
    check_in_date = request.data.get('checkInDate')
    check_out_date = request.data.get('checkOutDate')
    room_type = request.data.get('room_type')

    # List to store the response for each room type
    response_data = []

    # Assuming you have multiple room types to check
    if room_type:
        # Single room type case
        room = Room.objects.get(room_type=room_type)
        total_rooms = room.quantity

        overlapping_reservations = Reservation.objects.filter(
            Q(check_in_date__lte=check_out_date) & Q(check_out_date__gte=check_in_date),
            room_no=room
        ).aggregate(total_reserved_rooms=Sum('room_quantity'))

        reserved_rooms = overlapping_reservations['total_reserved_rooms'] or 0
        available_rooms = total_rooms - reserved_rooms

        # Serialize the room data
        room_serializer = RoomSerializer(room)

        # Append data for this room type
        response_data.append({
            "available_rooms": available_rooms,
            "room_data": room_serializer.data,
        })
    else:
        # Multiple room types case (you can iterate through multiple room types if needed)
        rooms = Room.objects.all()  # Assuming you want all rooms

        for room in rooms:
            total_rooms = room.quantity

            overlapping_reservations = Reservation.objects.filter(
                Q(check_in_date__lte=check_out_date) & Q(check_out_date__gte=check_in_date),
                room_no=room
            ).aggregate(total_reserved_rooms=Sum('room_quantity'))

            reserved_rooms = overlapping_reservations['total_reserved_rooms'] or 0
            available_rooms = total_rooms - reserved_rooms

            # Serialize the room data
            room_serializer = RoomSerializer(room)

            # Append data for each room type
            response_data.append({
                "available_rooms": available_rooms,
                "room_data": room_serializer.data,
            })

    return Response(response_data)

@api_view(["GET"])
def get_calculation_data(request):
    # Fetch all room data
    rooms = Room.objects.all()
    # Fetch all reservation data
    total_reservations = Reservation.objects.all()
    # Filter reservations booked on the current day
    today = timezone.now().date()
    reservations_today = Reservation.objects.filter(booked_on__date=today)
    # Count distinct customers based on their emails
    distinct_customers_count = Reservation.objects.values('email').distinct().count()
    # Calculate the total amount from all reservations
    total_amount = sum(int(reservation.amount) for reservation in total_reservations)
    # Prepare the response data
    response_data = {
        "total_rooms": rooms.count(),
        "total_reservations": total_reservations.count(),
        "reservations_today": reservations_today.count(),
        "total_amount": total_amount,
        "distinct_customers": distinct_customers_count,  # Count of distinct customers
    }

    return Response(response_data)

@api_view(["GET"])
def get_all_image(request):
    images = Images.objects.all()
    image_serializer = ImagesSerializer(images, many= True)
    
    return Response( image_serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_bed_type(request):
    bed_type = BedType.objects.all()
    bed_type_serializer = BedTypeSerializer(bed_type, many= True)
    
    return Response( bed_type_serializer.data, status=status.HTTP_200_OK)

@api_view(["GET"])
def get_room_size(request):
    size = RoomSize.objects.all()
    
    size_serializer = RoomSizeSerializer(size, many= True)
    
    return Response( size_serializer.data, status=status.HTTP_200_OK)



@api_view(["GET"])
def get_room_deatils(request, id):
    images = get_object_or_404(Room, room_type = id)
    image_serializer = RoomSerializer(images)
    
    return Response( image_serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_display_slider(request):
    displaySlider = DisplaySlider.objects.all()
    displaySlider_serializer = DisplaySliderSerializer(displaySlider, many = True)
    
    return Response( displaySlider_serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def add_display_slider(request):
    if request.method == 'POST':
        # Extract form fields
        room_no = request.POST.get('name')
        description = request.POST.get('description')
        button = request.POST.get('button')
        slider_image = request.FILES.get('image')

        # Extract features (JSON string to list)
       

        # Create and save the room object
        room = DisplaySlider(
            name=room_no, 
            description=description, 
            button_name=button, 
            slider_image = slider_image
        )
        room.save()

        # Save the images
        return JsonResponse({'message': 'Room created successfully!'})
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@api_view(["PUT"])
def update_display_slider(request,id):
    if request.method == 'PUT':
        # Extract form fields
        room_no = request.POST.get('name')
        description = request.POST.get('description')
        button = request.POST.get('button')
        slider_image = request.FILES.get('image')

        display = get_object_or_404(DisplaySlider, id=id)
        # Create and save the room object
        display.name=room_no
        display.button_name=button
        display.description=description
        display.save()

        if slider_image is not None:
            display.slider_image =slider_image
            display.save()
        
        # Add the features to the room
        
        return JsonResponse({'message': 'Display Slider updated successfully!'})
     
        
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@api_view(["DELETE"])
def detele_display_slider(request, id):
    display = get_object_or_404(DisplaySlider, id = id)
    display.delete()
    return Response({'message': 'Display Slider Deleted successfully!'}, status=status.HTTP_200_OK)




@api_view(["POST"])
def add_bedType(request):
    if request.method == 'POST':
        # Extract form fields
        bed_type = request.data.get('bedType')
        # Create and save the room object
        room = BedType(
            bed_type=bed_type, 
        )
        room.save()

        # Save the images
        return JsonResponse({'message': 'BedType created successfully!'})
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@api_view(["PUT"])
def update_BedType(request,id):
    if request.method == 'PUT':
        # Extract form fields
        bed_type = request.data.get('bedType')

        bedType = get_object_or_404(BedType, id=id)
        # Create and save the room object
        bedType.name=bed_type
        bedType.save()

        # Add the features to the room
        
        return JsonResponse({'message': 'Bed Type updated successfully!'})
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@api_view(["DELETE"])
def detele_BedType(request, id):
    display = get_object_or_404(BedType, id = id)
    display.delete()
    return Response({'message': 'Bed Type Deleted successfully!'}, status=status.HTTP_200_OK)




@api_view(["POST"])
def add_RoomSize(request):
    if request.method == 'POST':
        # Extract form fields
        size = request.data.get('roomSize')
        # Create and save the room object
        room = RoomSize(
            size=size, 
        )
        room.save()

        # Save the images
        return JsonResponse({'message': 'Room Size created successfully!'})
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@api_view(["PUT"])
def update_RoomSize(request,id):
    if request.method == 'PUT':
        # Extract form fields
        size = request.data.get('roomSize')

        bedType = get_object_or_404(RoomSize, id=id)
        # Create and save the room object
        bedType.size=size
        bedType.save()

        # Add the features to the room
        return JsonResponse({'message': 'Room Size updated successfully!'})
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@api_view(["DELETE"])
def detele_RoomSize(request, id):
    display = get_object_or_404(RoomSize, id = id)
    display.delete()
    return Response({'message': 'Room Size Deleted successfully!'}, status=status.HTTP_200_OK)



@api_view(["POST"])
def add_RoomFeature(request):
    if request.method == 'POST':
        # Extract form fields
        feature_name = request.POST.get('featureName')
        feature_image = request.FILES.get('image')
        print("feature_image",feature_image)
        # Create and save the room object
        feature = FeatureList(
            feature_name=feature_name, 
            feature_images = feature_image
        )
        feature.save()

        # Save the images
        return JsonResponse({'message': 'Room Size created successfully!'})
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@api_view(["PUT"])
def update_RoomFeature(request,id):
    if request.method == 'PUT':
        # Extract form fields
        feature_name = request.data.get('featureName')
        feature_image = request.FILES.get('image')

        fetaure = get_object_or_404(FeatureList, id=id)
        # Create and save the room object
        fetaure.feature_name=feature_name
        fetaure.save()

        if feature_image is not None:
            fetaure.feature_images = feature_image
            fetaure.save()

        # Add the features to the room
        return JsonResponse({'message': 'Room Size updated successfully!'})
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@api_view(["DELETE"])
def detele_RoomFeature(request, id):
    feature = get_object_or_404(FeatureList, id = id)
    feature.delete()
    return Response({'message': 'Room Size Deleted successfully!'}, status=status.HTTP_200_OK)




@api_view(["GET"])
def get_coordinates(request):
    address = request.GET.get('address')
    print("address",address)
    if not address:
        return JsonResponse({'error': 'Address parameter is missing'}, status=400)
    
    # URL encoding the address to avoid issues with special characters
    address = requests.utils.quote(address)
    url = f"https://nominatim.openstreetmap.org/search?q=Basundhara+Residential+Area&format=json"
    
    response = requests.get(url)
    
    if response.status_code == 200 and response.json():
        data = response.json()[0]
        return JsonResponse({"lat": data["lat"], "lng": data["lon"]})
    
    return JsonResponse({'error': 'Coordinates not found'}, status=404)







