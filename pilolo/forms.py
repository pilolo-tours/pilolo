from django import forms
from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['schedule', 'participants', 'tour_date', 'phone', 'special_requirements']
        widgets = {
            'schedule': forms.HiddenInput(),
            'tour_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'participants': forms.NumberInput(attrs={'min': 1, 'max': 8, 'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+233...'}),
            'special_requirements': forms.Textarea(attrs={'rows': 3, 'class': 'form-input'}),
        }