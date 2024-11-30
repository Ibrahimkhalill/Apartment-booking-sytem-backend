
from django.urls import path
from .views import * 
urlpatterns = [
   
   # path('',views.home, name='home'),
   path('', index, name='index'),
   path('send/otp/', send_otp, name='send_otp'),
   path('verify-otp/', verify_otp, name='verify_otp'),
   path('api/signup/', signup_view, name='signup'),
   path('api/login/',login_view,name='login'),
   path('api/check-auth/',check_auth,name='check-auth'),
   path('api/logout/',logout_api_view,name='logout'),
   path('api/pasword/changes',password_change,name='password-changes'),
   
   path('api/get_room/',get_room, name='get-room'),
   path('api/get_all_bed_type/',get_bed_type, name='get_all_bed_type'),
   path('api/get_all_size/',get_room_size, name='get-size'),
   path('api/get_feature/list/',get_feature_list, name='get-feature-list'),
   path('api/get/reservation/',get_reservation, name='get-reservation'),
   path('api/search/available/room/',available_room, name='available-room'),
   path('api/search/available/room/<int:room_id>/',available_room_by_id, name='available-room-id'),
   path('api/reservation/<int:room_id>',reservation,name='reservation'),
   path('release-room/<str:uuid>/', release_room, name='release_room'),
   path('confirmation_emai/',confirmation, name='confirmation'),
   path('api/book_room/', book_room, name="book-room"),
   path('api/get_booking/<str:uuid>/', get_booking, name="get-booking"),
   path('api/upadte_reservation/<int:id>/', update_reservation, name="upadte_reservation"),

   path('api/save-room/data/',add_room, name="save-room"),
   path('api/edit-room/<int:id>/',get_room_by_id, name="edit-room"),
   path('api/update-room/<int:id>/',updated_room, name="update-room"),
   path('api/delete/room/<int:id>/', detele_Room),

   path('api/get_available_rooms/',get_available_rooms, name="get_available-room"),


   path('api/get-all-calculatioin/',get_calculation_data,name='get-all'),
   path('api/get-all-images/',get_all_image,name='get-all-images'),
   path('api/get-room-details/<str:id>',get_room_deatils,name='get-room-deatils'),

   path ('api/add/display-slider/', add_display_slider),
   path ('api/get/display-slider/', get_display_slider),
   path ('api/update/display-slider/<int:id>/', update_display_slider),
   path ('api/delete/display-slider/<int:id>/', detele_display_slider),


   path ('api/add/bed-type/', add_bedType),
   path ('api/update/bed-type/<int:id>/', update_BedType),
   path ('api/delete/bed-type/<int:id>/', detele_BedType),

   path ('api/add/room-size/', add_RoomSize),
   path ('api/update/room-size/<int:id>/', update_RoomSize),
   path ('api/delete/room-size/<int:id>/', detele_RoomSize),

   path ('api/add/room-feature/', add_RoomFeature),
   path ('api/update/room-feature/<int:id>/', update_RoomFeature),
   path ('api/delete/room-feature/<int:id>/', detele_RoomFeature),
   
   path ('api/delete/room/<int:room_id>/feature/<int:feature_id>/', delete_feature_from_room),
   path ('api/delete/room/image/<int:image_id>/', delete_image_from_room),

    path('api/get-coordinates/', get_coordinates, name='get_coordinates'),

   # path('get_date',views.get_date,name='get_date'),
   # path('available_room/',views.available_room,name="available_room"),


   # path('contactapi/', views.ContactList.as_view()),
   # path('api_detail/<int:pk>/', views.ContactDetail.as_view()),

   # path('index/',weather_views.index,name='index')
]
