from django import forms
from .models import Booking, Appointment

class BookingForm(forms.ModelForm):
    website_url = forms.CharField(required=False) # Honeypot

    class Meta:
        model = Booking
        fields = ['name', 'email', 'phone', 'service', 'message']

class AppointmentForm(forms.ModelForm):
    website_url = forms.CharField(required=False) # Honeypot

    class Meta:
        model = Appointment
        fields = ['name', 'email', 'phone', 'date', 'time_slot']
