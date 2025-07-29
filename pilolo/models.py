from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone

# Create your models here.
class UserManager(BaseUserManager):
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
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        db_table = 'user'




class Tour(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    duration = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    max_participants = models.IntegerField(default=8)
    highlights = models.TextField()
    what_included = models.TextField()
    what_to_bring = models.TextField()
    meeting_point = models.CharField(max_length=200)
    image = models.URLField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Tour'
        verbose_name_plural = 'Tours'
        db_table = 'tour'


class TourSchedule(models.Model):
    DAYS_OF_WEEK = [
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]
    
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='schedules')
    day = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    def __str__(self):
        return f"{self.tour.name} - {self.day} {self.start_time}"
    
    class Meta:
        verbose_name = 'Tour Schedule'
        verbose_name_plural = 'Tour Schedules'
        db_table = 'tour_schedule'
    

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    schedule = models.ForeignKey(TourSchedule, on_delete=models.CASCADE)
    participants = models.IntegerField(default=1)
    booking_date = models.DateTimeField(auto_now_add=True)
    tour_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    phone = models.CharField(max_length=20)
    special_requirements = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.schedule.tour.name}"
    
    class Meta:
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        db_table = 'booking'
        ordering = ['-booking_date']