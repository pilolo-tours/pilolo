from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('tour/<int:tour_id>/', views.tour_detail, name='tour_detail'),
    path('booking-form/', views.booking_form, name='booking_form'),
    path('create-booking/', views.create_booking, name='create_booking'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
]