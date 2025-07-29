from django.contrib import admin
from .models import Tour, TourSchedule, Booking

@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'duration', 'max_participants']
    search_fields = ['name', 'description']

@admin.register(TourSchedule)
class TourScheduleAdmin(admin.ModelAdmin):
    list_display = ['tour', 'day', 'start_time', 'end_time']
    list_filter = ['day', 'tour']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'schedule', 'tour_date', 'participants', 'status']
    list_filter = ['status', 'tour_date']
    search_fields = ['user__username', 'schedule__tour__name']