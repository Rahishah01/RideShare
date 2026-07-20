from django import forms
from .models import Trip
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True
    )

    class Meta:
        model = User

        fields = [
            "username",
            "email",
            "password1",
            "password2",
        ]

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(
            email__iexact=email
        ).exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )

        return email



class TripForm(forms.ModelForm):
    class Meta:
        model = Trip

        fields = [
            "start_location",
            "end_location",
            "date",
            "time",
            "seats_available",
            "price_per_seat",
        ]

        labels = {
            "start_location": "Leaving from",
            "end_location": "Going to",
            "date": "Travel date",
            "time": "Departure time",
            "seats_available": "Available seats",
            "price_per_seat": "Price per seat",
        }

        widgets = {
            "start_location": forms.TextInput(
                attrs={
                    "placeholder": "Example: Chicago",
                    "autocomplete": "off",
                }
            ),
            "end_location": forms.TextInput(
                attrs={
                    "placeholder": "Example: Madison",
                    "autocomplete": "off",
                }
            ),
            "date": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
            "time": forms.TimeInput(
                attrs={
                    "type": "time",
                }
            ),
            "seats_available": forms.NumberInput(
                attrs={
                    "min": "1",
                    "max": "20",
                    "placeholder": "Example: 3",
                }
            ),
            "price_per_seat": forms.NumberInput(
                attrs={
                    "min": "0",
                    "step": "0.01",
                    "placeholder": "Example: 25.00",
                }
            ),
        }

    def clean_seats_available(self):
        seats = self.cleaned_data["seats_available"]

        if seats < 1:
            raise forms.ValidationError(
                "At least one seat must be available."
            )

        if seats > 20:
            raise forms.ValidationError(
                "You can list a maximum of 20 seats."
            )

        return seats

    def clean_price_per_seat(self):
        price = self.cleaned_data["price_per_seat"]

        if price < 0:
            raise forms.ValidationError(
                "The price cannot be negative."
            )

        return price
    

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User

        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
        ]

        labels = {
            "username": "Username",
            "first_name": "First name",
            "last_name": "Last name",
            "email": "Email address",
        }

        widgets = {
            "username": forms.TextInput(
                attrs={
                    "placeholder": "Your username",
                    "autocomplete": "username",
                }
            ),
            "first_name": forms.TextInput(
                attrs={
                    "placeholder": "Your first name",
                    "autocomplete": "given-name",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "placeholder": "Your last name",
                    "autocomplete": "family-name",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "placeholder": "you@example.com",
                    "autocomplete": "email",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.get("instance")
        super().__init__(*args, **kwargs)

        self.fields["email"].required = True

    def clean_username(self):
        username = self.cleaned_data["username"].strip()

        existing_user = User.objects.filter(
            username__iexact=username
        )

        if self.current_user:
            existing_user = existing_user.exclude(
                id=self.current_user.id
            )

        if existing_user.exists():
            raise forms.ValidationError(
                "This username is already being used."
            )

        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        existing_user = User.objects.filter(
            email__iexact=email
        )

        if self.current_user:
            existing_user = existing_user.exclude(
                id=self.current_user.id
            )

        if existing_user.exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )

        return email