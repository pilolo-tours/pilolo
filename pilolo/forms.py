from django import forms
from allauth.account.forms import SignupForm

from pilolo.models import Booking


class BookingForm(forms.ModelForm):
    participants = forms.IntegerField(
        min_value=0,
        widget=forms.HiddenInput(),
        initial=0 
    )

    class Meta:
        model = Booking
        fields = ['schedule', 'participants', 'special_requirements']
        widgets = {
            'schedule': forms.HiddenInput(),
            'special_requirements': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 mt-1 text-gray-700 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition duration-200',
                'rows': 3,
                'placeholder': 'Any special needs or requests...'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['participants'].initial = 0
        


    def clean(self):
        cleaned_data = super().clean()
        participants = cleaned_data.get('participants', 0)
        schedule = cleaned_data.get('schedule')

        if schedule:
            # Total people = 1 (booker) + participants
            print(f"Total participants including booker: {participants}")
            print(f"Remaining slots in schedule: {schedule.remaining_slots}")
            if (participants) > schedule.remaining_slots:
                self.add_error('participants', 
                    f"Only {schedule.remaining_slots} total spots available (including yourself).")
        
        return cleaned_data





class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='First Name')
    last_name = forms.CharField(max_length=30, label='Last Name')
    phone_number = forms.CharField(max_length=15, label='Phone Number', required=False)

    def save(self, request):
        # Ensure you call the parent class's save.
        # .save() returns a User object.
        user = super(CustomSignupForm, self).save(request)

        # Add your custom fields to the user object.
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone_number = self.cleaned_data['phone_number']

        # Save the user with the new data.
        user.save()

        # You must return the user object.
        return user