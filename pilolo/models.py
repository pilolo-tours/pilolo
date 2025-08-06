from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.forms import ValidationError
from django.utils import timezone

# Create your models here.
class UserManager(BaseUserManager):
    """Custom manager for the CustomUser model."""
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """Custom user model for the application."""
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    username = models.CharField(max_length=50, unique=True, blank=True, null=True, default=None)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        db_table = 'user'


class Tour(models.Model):
    """Model representing a tour."""
    name = models.CharField(max_length=200)
    description = models.TextField()
    duration = models.IntegerField(help_text="Duration in hours", default=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    max_participants = models.IntegerField(default=8)
    highlights = models.TextField()
    what_included = models.TextField()
    what_to_bring = models.TextField()
    meeting_point = models.CharField(max_length=200)
    image = models.URLField(blank=True)

    def highlights_as_list(self):
        return [h.strip() for h in self.highlights.split('\n') if h.strip()]

    def what_included_as_list(self):
        return [i.strip() for i in self.what_included.split('\n') if i.strip()]

    def what_to_bring_as_list(self):
        return [b.strip() for b in self.what_to_bring.split('\n') if b.strip()]
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Tour'
        verbose_name_plural = 'Tours'
        db_table = 'tour'




class TourSchedule(models.Model):
    """Model representing a schedule for a tour."""
    DAYS_OF_WEEK = [
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]

    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='schedules')
    day = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    date = models.DateField(default=timezone.now)
    start_time = models.TimeField()
    end_time = models.TimeField()


    # Count the number of booked participants for this schedule
    @property
    def booked_count(self):
        confirmed_bookings = self.bookings.filter(status='confirmed')
        participants = sum(booking.participant_details.count() for booking in confirmed_bookings)

        # return participants and the booker
        return participants + confirmed_bookings.count()


    # Calculate the remaining slots for this schedule
    @property
    def remaining_slots(self):
        return self.tour.max_participants - self.booked_count

    # Check if the schedule is fully booked
    @property
    def is_fully_booked(self):
        return self.remaining_slots == 0

    def __str__(self):
        return f"{self.tour.name} - {self.day} {self.start_time}"

    class Meta:
        verbose_name = 'Tour Schedule'
        verbose_name_plural = 'Tour Schedules'
        db_table = 'tour_schedule'


def unique_reference(length=12):
    """Generate a unique reference code for bookings."""
    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    reference = models.CharField(max_length=100, unique=True, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    schedule = models.ForeignKey(TourSchedule, on_delete=models.CASCADE, related_name='bookings')
    booking_date = models.DateTimeField(auto_now_add=True)
    tour_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    special_requirements = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.email} - {self.schedule.tour.name}"

    @property
    def participant_count(self):
        return self.participant_details.count()

    @property
    def total_price(self):
        participant_and_booker_count = self.participant_count + 1  # Include the booker
        return participant_and_booker_count * self.schedule.tour.price

    def clean(self):
        # Only validate if this is an existing booking
        if self.pk and self.status != 'cancelled':
            if self.participant_details.count() > self.schedule.remaining_slots:
                raise ValidationError(
                    f"Only {self.schedule.remaining_slots} slot(s) available for this tour."
                )

    def save(self, *args, **kwargs):
        # Set tour_date from schedule if not set
        if not self.tour_date and self.schedule:
            self.tour_date = self.schedule.date
        
        # Generate a unique reference if not already set
        if not self.reference:
            #check if there is a booking with the same reference
            while True:
                self.reference = unique_reference()
                if not Booking.objects.filter(reference=self.reference).exists():
                    break

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        db_table = 'booking'
        ordering = ['-booking_date']

        
class BookingParticipant(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='participant_details')
    full_name = models.CharField(max_length=100)
    age = models.PositiveIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.full_name} (Booking #{self.booking.id})"
    

    class Meta:
        verbose_name = 'Booking Participant'
        verbose_name_plural = 'Booking Participants'
        db_table = 'booking_participant'
        ordering = ['full_name']

class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, unique=True, blank=True)

    def __str__(self):
        return f"Payment for Booking #{self.booking.id} - {self.status}"

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        db_table = 'payment'

