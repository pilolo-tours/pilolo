from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('tour/<int:tour_id>/', views.tour_detail, name='tour_detail'),
    # path('booking-form/', views.booking_form, name='booking_form'),
    # path('create-booking/', views.create_booking, name='create_booking'),
    path('bookings/', views.my_bookings, name='my_bookings'),
    # path('participant-info/', views.participant_info_step, name='participant_info_step'),
    # path('payment/', views.payment_step, name='payment_step'), 

    path('book/schedule/<int:schedule_id>/', views.booking_start, name='booking_start'),
    path('book/participants/', views.booking_participants, name='booking_participants'),
    path('book/schedule/payment/', views.booking_payment, name='booking_payment'),
    path('book/confirmation/<str:reference>/', views.booking_confirmation, name='booking_confirmation'),
    path('bookings/<int:booking_id>/', views.booking_details, name='booking_details'),
    path('update-participant-count/', views.update_participant_count, name='update_participant_count'),
    path('tours/', views.tour_list, name='tours_list'),
]