from django.contrib import admin
from .models import BookingParticipant, CustomUser, Payment, Tour, TourSchedule, Booking

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
    list_display = ['user', 'schedule', 'tour_date', 'status']
    list_filter = ['status', 'tour_date']
    search_fields = ['user__username', 'schedule__tour__name']


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name']
    search_fields = ['email', 'first_name', 'last_name']

@admin.register(BookingParticipant)
class BookingParticipantAdmin(admin.ModelAdmin):
    list_display = ['booking', 'full_name', 'age', 'notes']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['booking', 'amount', 'payment_date', 'status']
    list_filter = ['status', 'payment_date']
    search_fields = ['booking__user__email', 'transaction_id']
