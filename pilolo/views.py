from django.utils import timezone
import json
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from .models import BookingParticipant, Payment, Tour, TourSchedule, Booking
from .forms import BookingForm
from django.template.loader import render_to_string
import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.paginator import Paginator



logger = logging.getLogger(__name__)


def home(request):
    tours = Tour.objects.all()[:5]  # Limit to 5 tours for the home page
    logger.info(f"Loaded {tours.count()} tours for home page")
    if not tours:
        messages.info(request, "No tours available at the moment. Please check back later.")
    return render(request, 'pilolo/home.html', {'tours': tours})


def tour_detail(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)
    schedules = tour.schedules.all()
    if not schedules:
        messages.info(request, "No schedules available for this tour. Please check back later.")
    return render(request, 'pilolo/tour_details.html', {
        'tour': tour,
        'schedules': schedules
    })


@require_http_methods(["GET", "POST"])
@login_required(login_url='account_login', redirect_field_name='next')
def booking_start(request, schedule_id):
    schedule = get_object_or_404(TourSchedule, id=schedule_id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST, initial={'schedule': schedule}, user=request.user)
        if form.is_valid():
            print("PART", form.cleaned_data['participants'])
            request.session['booking'] = {
                'schedule_id': schedule.id,
                'participants': form.cleaned_data['participants'],
                'special_requirements': form.cleaned_data['special_requirements'],
            } 
            print(form.cleaned_data['participants'])

            if form.cleaned_data['participants'] == 0:
                return redirect('booking_payment')

            return redirect('booking_participants')
    else:
        form = BookingForm(initial={
            'schedule': schedule,
        }, user=request.user)

    return render(request, 'pilolo/booking/start.html', {
        'form': form,
        'schedule': schedule,
        'tour': schedule.tour,
    })



@login_required(login_url='account_login')
def booking_participants(request):
    # Get booking data from session
    booking_data = request.session.get('booking')
    if not booking_data:
        messages.error(request, "No booking data found. Please start over.")
        return redirect('home')

    schedule = get_object_or_404(TourSchedule, id=booking_data['schedule_id'])
    participant_count = int(booking_data['participants'])
    print(f"Participant count from session: {participant_count}")
    tour = schedule.tour
    participants = []


    print(participant_count)
    # Handle case with additional participants
    if request.method == 'POST':
        if participant_count > 0:
            has_errors = False

            for i in range(1, participant_count+1):  # Start from 1 to match form field names
                full_name = request.POST.get(f'participant_{i}_full_name', '').strip()
                age = request.POST.get(f'participant_{i}_age', '').strip()
                notes = request.POST.get(f'participant_{i}_notes', '').strip()
                 
                if not full_name:
                     has_errors = True
                     messages.error(request, f"Please enter name for participant {i}")
                 
                participants.append({
                     'full_name': full_name,
                     'age': age,
                     'notes': notes,
                })

            print("Participants:", participants)


            if has_errors:
                 return render(request, 'pilolo/booking/booking_process.html', {
                     'participant_range': range(1, participant_count),
                     'participant_count': participant_count,
                     'remaining_slots': schedule.remaining_slots,
                     'schedule': schedule,
                     'tour': tour,
                     'step': 'participants',
                     'participants_data': participants  # Return data to repopulate form
                 })

        # store participants in session
        request.session['participants'] = participants
        
        return redirect('booking_payment')

    # GET request - show participant form
    return render(request, 'pilolo/booking/booking_process.html', {
        'step': 'participants',
        'participant_range': range(1, participant_count+1),
        'participant_count': participant_count,
        'participants_with_booker': participant_count + 1,  # Include the booker
        'remaining_slots': schedule.remaining_slots,
        'schedule': schedule,
        'tour': tour
    })


@login_required(login_url='account_login')
def booking_payment(request):
    booking_data = request.session.get('booking')
    if not booking_data:
        messages.error(request, "No booking data found. Please start over.")
        return redirect('home')
    participants_data = request.session.get('participants', [])
    participant_count = len(participants_data)
    schedule = get_object_or_404(TourSchedule, id=booking_data['schedule_id'])
    tour = schedule.tour
   

    if request.method == 'POST':
        data = request.body.decode('utf-8')
        data = json.loads(data) if data else {}
        payment_success = data.get('paymentSuccess', False)
        transaction_reference = data.get('reference', None)
        booking = Booking.objects.create(
            user=request.user,
            schedule=schedule,
            tour_date=schedule.date,
            special_requirements=booking_data['special_requirements'],
            status='confirmed',
        )

        if participants_data:
            for p in participants_data:
                BookingParticipant.objects.create(
                    booking=booking,
                    full_name=p['full_name'],
                    age=p['age'] if p['age'] else None,
                    notes=p['notes']
                )
        
        # save payment details
        Payment.objects.get_or_create(
            booking=booking,
            amount=booking.total_price,
            payment_date=timezone.now(),
            status= 'completed' if payment_success else 'failed',
            transaction_id=transaction_reference if payment_success else None
        )

        # send confirmation email
        if payment_success:
            try:
                send_booking_confirmation_email(request, booking)
            except Exception as e:
                logger.error(f"Failed to send confirmation email: {str(e)}")
                # Don't fail the booking if email fails, just log it
            messages.success(request, "Booking successful! A confirmation email has been sent to you.")
        return redirect('booking_confirmation', reference=booking.reference)

    return render(request, 'pilolo/booking/booking_process.html', {
        'schedule': schedule,
        'step': 'payment',
        'tour': tour,
        'paystack_key': settings.PAYSTACK_API_PUBLIC_KEY,
        'participant_count': participant_count,
        'total_price': tour.price * (participant_count + 1) if participant_count > 0 else tour.price,
        'special_requirements': booking_data['special_requirements'],
        'participants_data': participants_data  # Pass data to payment step
    })

def send_booking_confirmation_email(request, booking):
    """Send booking confirmation email to the user"""
    subject = f"Your Tour Booking Confirmation - {booking.schedule.tour.name}"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [booking.user.email]
    
    # Prepare context for the email template
    context = {
        'user': booking.user,
        'booking': booking,
        'tour': booking.schedule.tour,
        'schedule': booking.schedule,
        'participants': booking.participant_details.all(),
        'total_price': booking.total_price,
        'site_name': request.get_host(),
    }
    
    # Render email templates
    text_content = render_to_string('emails/booking_confirmation.txt', context)
    html_content = render_to_string('emails/booking_confirmation.html', context)
    
    # Create and send email
    email = EmailMultiAlternatives(
        subject,
        text_content,
        from_email,
        recipient_list
    )
    email.attach_alternative(html_content, "text/html")
    email.send()

@login_required(login_url='account_login')
def booking_confirmation(request, reference):
    booking = get_object_or_404(Booking, reference=reference)
    schedule = booking.schedule
    participant_count = booking.participant_details.count()
    special_requirements = booking.special_requirements
    participants_data = booking.participant_details.all()

    if not schedule:
        return redirect('home')

    schedule = get_object_or_404(TourSchedule, id=schedule.id)

    # Clear booking-related session data after confirmation
    if 'booking' in request.session:
        del request.session['booking']
    if 'participants' in request.session:
        del request.session['participants']

    return render(request, 'pilolo/booking/booking_process.html', {
        'schedule': schedule,
        'step': 'confirmation',
        'participant_count': participant_count,
        'special_requirements': special_requirements,
        'participants_data': participants_data,
        'booking': booking,
    })

@login_required(login_url='account_login')
def booking_details(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    payment = booking.payments.first()
    context = {
        'booking': booking,
        'tour': booking.schedule.tour,
        'schedule': booking.schedule,
        'participants': booking.participant_details.all(),
        'payment': payment
    }
    
    return render(request, 'pilolo/booking/details.html', context)




@login_required(login_url='account_login')
def my_bookings(request):
    # Get status from request (default to 'all')
    status = request.GET.get('status', 'all')
    
    # Base queryset
    bookings_list = Booking.objects.filter(user=request.user).order_by('-booking_date')
    
    # Apply status filter if not 'all'
    if status == 'upcoming':
        bookings_list = bookings_list.filter(status__in=['confirmed', 'pending'], tour_date__gte=timezone.now().date())
    elif status == 'confirmed':
        bookings_list = bookings_list.filter(status='confirmed')
        print(f"Filtered bookings for completed status: {bookings_list.count()}")
    elif status == 'cancelled':
        bookings_list = bookings_list.filter(status='cancelled')
    
    # Pagination
    paginator = Paginator(bookings_list, 10)  # Show 10 bookings per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('HX-Request'):
        # Return just the bookings list partial for HTMX requests
        return render(request, 'pilolo/partials/bookings_list.html', {
            'bookings': page_obj,
            'is_paginated': page_obj.has_other_pages(),
            'page_obj': page_obj,
            'current_status': status
        })
    
    return render(request, 'pilolo/my_bookings.html', {
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'bookings': page_obj,  # For backward compatibility
        'current_status': status  # Pass the current status to template
    })

def update_participant_count(request):
    logger.info("Updating participant count")
    if request.method == 'POST':
        data = json.loads(request.body)
        count = data.get('count', 0)
        request.session['booking']['participants'] = count
        request.session.modified = True

        logger.info(f"Participant count updated to {count}")
        print(f"Participant count updated to {count}")

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)


def tour_list(request):
    tours = Tour.objects.all().order_by('name')
    
    # Handle search
    if 'search' in request.GET:
        search_term = request.GET['search']
        tours = tours.filter(name__icontains=search_term)
        if not tours:
            messages.info(request, "No tours found matching your search criteria.")
    
    # Pagination
    paginator = Paginator(tours, 9)  # Show 9 tours per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'pilolo/tour_list.html', {
        'page_obj': page_obj,
        'tours': page_obj,  # For backward compatibility
        'is_paginated': page_obj.has_other_pages(),
    })