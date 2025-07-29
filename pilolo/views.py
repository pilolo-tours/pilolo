from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.template.loader import render_to_string, get_template
from .models import Tour, TourSchedule, Booking
from .forms import BookingForm
# import csrf decorator
from django.views.decorators.csrf import csrf_exempt


def home(request):
    tours = Tour.objects.all()
    return render(request, 'pilolo/home.html', {'tours': tours})

def tour_detail(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)
    schedules = tour.schedules.all()
    return render(request, 'pilolo/tour_details.html', {
        'tour': tour,
        'schedules': schedules
    })

@require_http_methods(["POST"])
@csrf_exempt
def booking_form(request):
    schedule_id = request.POST.get('schedule_id')
    schedule = get_object_or_404(TourSchedule, id=schedule_id)
    form = BookingForm()
    
    # return html to render
    return render(request, 'pilolo/partials/booking_form.html', {
        'form': form,
        'schedule': schedule,
        'request': request
    })



@login_required
@require_http_methods(["POST"])
def create_booking(request):
    form = BookingForm(request.POST)
    if form.is_valid():
        booking = form.save(commit=False)
        booking.user = request.user
        booking.save()
        messages.success(request, 'Your booking has been confirmed!')
        return JsonResponse({
            'success': True,
            'message': 'Booking confirmed successfully!'
        })
    else:
        
        return render(request, 'pilolo/partials/booking_form.html', {
            'form': form})

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    return render(request, 'pilolo/my_bookings.html', {'bookings': bookings})
