from django.contrib import admin

# Register your models here.

from mainapp.models import *
class ImagesInline(admin.TabularInline):
    model = Images
    extra = 1  # Number of empty image fields to sho

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_no', 'room_type', 'is_available', 'price']
    search_fields = ['room_no', 'room_type']
    list_filter = ['is_available']
    filter_horizontal = ['features']
    inlines = [ImagesInline]  # Add the inline for Images

admin.site.register(Reservation)
admin.site.register(Contact)
@admin.register(FeatureList)
class FeatureListAdmin(admin.ModelAdmin):
    list_display = ['feature_name']
    search_fields = ['feature_name']

@admin.register(Images)
class ImagesAdmin(admin.ModelAdmin):
    list_display = ['room', 'room_image']
    
admin.site.register(PreBooking)
admin.site.register(RoomSize)
admin.site.register(BedType)
admin.site.register(OTP)
admin.site.register(CustomeUser)
admin.site.register(DisplaySlider)