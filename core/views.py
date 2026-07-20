from django.shortcuts import render, redirect
from .models import Trip, Booking, Review
from .forms import TripForm, SignUpForm, ProfileForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.db import transaction
from decimal import Decimal
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User



def home(request):
    trips = Trip.objects.all()

    from_location = request.GET.get('from')
    to_location = request.GET.get('to')
    date = request.GET.get('date')

    if from_location:
        trips = trips.filter(start_location__icontains=from_location)

    if to_location:
        trips = trips.filter(end_location__icontains=to_location)

    if date:
        trips = trips.filter(date=date)

    return render(request, 'home.html', {'trips': trips})


@login_required
def create_trip(request):
    if request.method == "POST":
        form = TripForm(request.POST)

        if form.is_valid():
            trip = form.save(commit=False)
            trip.driver = request.user
            trip.save()

            messages.success(
                request,
                "Your ride was published successfully."
            )

            return redirect("dashboard")
    else:
        form = TripForm()

    return render(
        request,
        "create_trip.html",
        {
            "form": form,
        },
    )

def signup(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = SignUpForm(request.POST)

        if form.is_valid():
            user = form.save()

            login(request, user)

            messages.success(
                request,
                "Your account was created successfully."
            )

            return redirect("home")
    else:
        form = SignUpForm()

    return render(
        request,
        "signup.html",
        {
            "form": form,
        }
    )

@login_required
def book_trip(request, trip_id):
    if request.method != "POST":
        return redirect(
            "trip_detail",
            trip_id=trip_id,
        )

    try:
        seats_requested = int(
            request.POST.get("seats", 1)
        )
    except (TypeError, ValueError):
        messages.error(
            request,
            "Please enter a valid number of seats.",
        )

        return redirect(
            "trip_detail",
            trip_id=trip_id,
        )

    if seats_requested < 1:
        messages.error(
            request,
            "You must reserve at least one seat.",
        )

        return redirect(
            "trip_detail",
            trip_id=trip_id,
        )

    with transaction.atomic():
        trip = get_object_or_404(
            Trip.objects.select_for_update(),
            id=trip_id,
        )

        if trip.driver == request.user:
            messages.error(
                request,
                "You cannot book your own ride.",
            )

            return redirect(
                "trip_detail",
                trip_id=trip.id,
            )

        if trip.seats_available <= 0:
            messages.error(
                request,
                "This ride is fully booked.",
            )

            return redirect(
                "trip_detail",
                trip_id=trip.id,
            )

        if seats_requested > trip.seats_available:
            messages.error(
                request,
                (
                    f"Only {trip.seats_available} "
                    "seat(s) are currently available."
                ),
            )

            return redirect(
                "trip_detail",
                trip_id=trip.id,
            )

        booking, created = Booking.objects.get_or_create(
            trip=trip,
            passenger=request.user,
            defaults={
                "seats_booked": seats_requested,
            },
        )

        if not created:
            booking.seats_booked += seats_requested

            booking.save(
                update_fields=["seats_booked"],
            )

        trip.seats_available -= seats_requested

        trip.save(
            update_fields=["seats_available"],
        )

    if created:
        messages.success(
            request,
            (
                f"You successfully booked "
                f"{seats_requested} seat(s)."
            ),
        )
    else:
        messages.success(
            request,
            (
                f"{seats_requested} additional seat(s) "
                "were added to your booking."
            ),
        )

    return redirect("my_bookings")


@login_required
def my_bookings(request):
    bookings = (
        Booking.objects
        .filter(passenger=request.user)
        .select_related("trip", "trip__driver")
    )

    total_seats_reserved = sum(
        booking.seats_booked
        for booking in bookings
    )

    return render(
        request,
        "my_bookings.html",
        {
            "bookings": bookings,
            "total_seats_reserved": total_seats_reserved,
        },
    )


@login_required
def driver_dashboard(request):
    trips = (
        Trip.objects
        .filter(driver=request.user)
        .order_by("date", "time", "id")
    )

    total_earnings = 0
    platform_earnings = 0
    total_bookings = 0
    total_available_seats = 0

    commission_rate = Decimal("0.10")

    for trip in trips:
        total_available_seats += trip.seats_available

        bookings = Booking.objects.filter(trip=trip)

        for booking in bookings:
            booking_total = (
                booking.seats_booked *
                trip.price_per_seat
            )

            commission = (
                booking_total *
                commission_rate
            )

            driver_amount = (
                booking_total -
                commission
            )

            total_earnings += driver_amount
            platform_earnings += commission
            total_bookings += booking.seats_booked

    context = {
        "trips": trips,
        "total_trips": trips.count(),
        "total_earnings": total_earnings,
        "platform_earnings": platform_earnings,
        "total_bookings": total_bookings,
        "total_available_seats": total_available_seats,
    }

    return render(
        request,
        "driver_dashboard.html",
        context,
    )


@login_required
def edit_trip(request, trip_id):
    trip = get_object_or_404(
        Trip,
        id=trip_id,
        driver=request.user,
    )

    if request.method == "POST":
        form = TripForm(
            request.POST,
            instance=trip,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Your ride was updated successfully.",
            )

            return redirect("dashboard")
    else:
        form = TripForm(instance=trip)

    return render(
        request,
        "edit_trip.html",
        {
            "form": form,
            "trip": trip,
        },
    )


@login_required
def delete_trip(request, trip_id):
    trip = get_object_or_404(
        Trip,
        id=trip_id,
        driver=request.user,
    )

    if request.method != "POST":
        return redirect("dashboard")

    route = (
        f"{trip.start_location} "
        f"to {trip.end_location}"
    )

    trip.delete()

    messages.success(
        request,
        f"{route} was deleted successfully.",
    )

    return redirect("dashboard")


@login_required
def add_review(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)

    if request.method == 'POST':
        rating = int(request.POST.get('rating'))
        comment = request.POST.get('comment', '')

        Review.objects.create(
            trip=trip,
            reviewer=request.user,
            rating=rating,
            comment=comment
        )

        return redirect('home')

    return render(request, 'add_review.html', {'trip': trip})


@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related(
            "trip",
            "trip__driver",
        ),
        id=booking_id,
        passenger=request.user,
    )

    if request.method == "POST":
        try:
            seats_to_cancel = int(
                request.POST.get("seats", 0)
            )
        except (TypeError, ValueError):
            messages.error(
                request,
                "Please enter a valid number of seats.",
            )

            return redirect(
                "cancel_booking",
                booking_id=booking.id,
            )

        if seats_to_cancel < 1:
            messages.error(
                request,
                "You must cancel at least one seat.",
            )

            return redirect(
                "cancel_booking",
                booking_id=booking.id,
            )

        if seats_to_cancel > booking.seats_booked:
            messages.error(
                request,
                (
                    f"You only have "
                    f"{booking.seats_booked} "
                    "seat(s) booked."
                ),
            )

            return redirect(
                "cancel_booking",
                booking_id=booking.id,
            )

        with transaction.atomic():
            booking = get_object_or_404(
                Booking.objects.select_for_update(),
                id=booking_id,
                passenger=request.user,
            )

            trip = Trip.objects.select_for_update().get(
                id=booking.trip_id
            )

            if seats_to_cancel >= booking.seats_booked:
                restored_seats = booking.seats_booked

                booking.delete()

                trip.seats_available += restored_seats

                messages.success(
                    request,
                    "Your booking was fully cancelled.",
                )
            else:
                booking.seats_booked -= seats_to_cancel
                booking.save(
                    update_fields=["seats_booked"]
                )

                trip.seats_available += seats_to_cancel

                messages.success(
                    request,
                    (
                        f"{seats_to_cancel} seat(s) "
                        "were cancelled successfully."
                    ),
                )

            trip.save(
                update_fields=["seats_available"]
            )

        return redirect("my_bookings")

    return render(
        request,
        "cancel_booking.html",
        {
            "booking": booking,
        },
    )


def trip_detail(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)
    reviews = Review.objects.filter(trip=trip)

    return render(request, 'trip_detail.html', {
        'trip': trip,
        'reviews': reviews
    })

def find_rides(request):
    trips = Trip.objects.all().order_by("date", "time")

    from_loc = request.GET.get("from", "").strip()
    to_loc = request.GET.get("to", "").strip()
    date = request.GET.get("date", "").strip()
    seats = request.GET.get("seats", "").strip()

    if from_loc:
        trips = trips.filter(
            start_location__icontains=from_loc
        )

    if to_loc:
        trips = trips.filter(
            end_location__icontains=to_loc
        )

    if date:
        trips = trips.filter(date=date)

    if seats:
        try:
            seats_needed = int(seats)

            if seats_needed > 0:
                trips = trips.filter(
                    seats_available__gte=seats_needed
                )

        except ValueError:
            pass

    return render(
        request,
        "find_rides.html",
        {
            "trips": trips,
        }
    )

@login_required
def profile(request):
    user = request.user

    offered_trips = Trip.objects.filter(
        driver=user
    )

    passenger_bookings = (
        Booking.objects
        .filter(passenger=user)
        .select_related("trip")
    )

    total_seats_reserved = sum(
        booking.seats_booked
        for booking in passenger_bookings
    )

    total_driver_earnings = 0
    commission_rate = Decimal("0.10")

    driver_bookings = (
        Booking.objects
        .filter(trip__driver=user)
        .select_related("trip")
    )

    for booking in driver_bookings:
        gross_amount = (
            booking.seats_booked *
            booking.trip.price_per_seat
        )

        total_driver_earnings += (
            gross_amount *
            (Decimal("1.00") - commission_rate)
        )

    if request.method == "POST":
        form = ProfileForm(
            request.POST,
            instance=user,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Your profile was updated successfully."
            )

            return redirect("profile")
    else:
        form = ProfileForm(instance=user)

    return render(
        request,
        "profile.html",
        {
            "form": form,
            "offered_trips_count": offered_trips.count(),
            "bookings_count": passenger_bookings.count(),
            "total_seats_reserved": total_seats_reserved,
            "total_driver_earnings": total_driver_earnings,
        },
    )

@login_required
def trip_passengers(request, trip_id):
    trip = get_object_or_404(
        Trip,
        id=trip_id,
        driver=request.user,
    )

    bookings = (
        Booking.objects
        .filter(trip=trip)
        .select_related("passenger")
        .order_by("passenger__username")
    )

    total_reserved_seats = sum(
        booking.seats_booked
        for booking in bookings
    )

    gross_earnings = sum(
        booking.seats_booked * trip.price_per_seat
        for booking in bookings
    )

    commission_rate = Decimal("0.10")
    platform_commission = (
        gross_earnings * commission_rate
    )

    driver_earnings = (
        gross_earnings - platform_commission
    )

    return render(
        request,
        "trip_passengers.html",
        {
            "trip": trip,
            "bookings": bookings,
            "total_passengers": bookings.count(),
            "total_reserved_seats": total_reserved_seats,
            "gross_earnings": gross_earnings,
            "platform_commission": platform_commission,
            "driver_earnings": driver_earnings,
        },
    )

#admin Dashboard

@staff_member_required
def admin_dashboard(request):

    users = User.objects.count()

    trips = Trip.objects.count()

    bookings = Booking.objects.count()

    reviews = Review.objects.count()

    total_seats = sum(
        booking.seats_booked
        for booking in Booking.objects.all()
    )

    gross_revenue = Decimal("0")

    for booking in Booking.objects.select_related("trip"):
        gross_revenue += (
            booking.trip.price_per_seat *
            booking.seats_booked
        )

    platform_fee = gross_revenue * Decimal("0.10")

    driver_income = gross_revenue - platform_fee

    context = {
        "users": users,
        "trips": trips,
        "bookings": bookings,
        "reviews": reviews,
        "total_seats": total_seats,
        "gross_revenue": gross_revenue,
        "platform_fee": platform_fee,
        "driver_income": driver_income,
        "recent_users": User.objects.order_by("-date_joined")[:5],
        "recent_trips": Trip.objects.order_by("-id")[:5],
        "recent_bookings": Booking.objects.order_by("-id")[:5],
    }

    return render(
        request,
        "admin_dashboard.html",
        context,
    )

@staff_member_required
def manage_users(request):

    users = User.objects.all().order_by("-date_joined")

    return render(
        request,
        "manage_users.html",
        {
            "users": users
        }
    )


@staff_member_required
def manage_trips(request):

    trips = Trip.objects.select_related("driver")

    return render(
        request,
        "manage_trips.html",
        {
            "trips": trips
        }
    )


@staff_member_required
def manage_bookings(request):

    bookings = Booking.objects.select_related(
        "trip",
        "passenger",
    )

    return render(
        request,
        "manage_bookings.html",
        {
            "bookings": bookings
        }
    )


@staff_member_required
def manage_reviews(request):

    reviews = Review.objects.select_related(
        "trip",
        "reviewer",
    )

    return render(
        request,
        "manage_reviews.html",
        {
            "reviews": reviews
        }
    )


