from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Trip(models.Model):
    driver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="offered_trips",
    )

    start_location = models.CharField(
        max_length=200,
        db_index=True,
    )

    end_location = models.CharField(
        max_length=200,
        db_index=True,
    )

    date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
    )

    time = models.TimeField(
        null=True,
        blank=True,
    )

    seats_available = models.PositiveIntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(20),
        ]
    )

    price_per_seat = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
        ],
    )

    created_at = models.DateTimeField(
        default=timezone.now,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "date",
            "time",
            "id",
        ]

        indexes = [
            models.Index(
                fields=[
                    "start_location",
                    "end_location",
                ]
            ),
            models.Index(
                fields=[
                    "date",
                    "time",
                ]
            ),
        ]

        constraints = [
            models.CheckConstraint(
                check=models.Q(
                    seats_available__gte=0
                ),
                name="trip_seats_not_negative",
            ),
            models.CheckConstraint(
                check=models.Q(
                    price_per_seat__gte=0
                ),
                name="trip_price_not_negative",
            ),
        ]

    def __str__(self):
        return (
            f"{self.start_location} → "
            f"{self.end_location}"
        )


class Booking(models.Model):
    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name="bookings",
    )

    passenger = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="ride_bookings",
    )

    seats_booked = models.PositiveIntegerField(
        default=1,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(20),
        ],
    )

    created_at = models.DateTimeField(
        default=timezone.now,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "-created_at",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "trip",
                    "passenger",
                ],
                name="one_booking_per_passenger_per_trip",
            ),
            models.CheckConstraint(
                check=models.Q(
                    seats_booked__gte=1
                ),
                name="booking_seats_at_least_one",
            ),
        ]

    @property
    def total_price(self):
        return (
            self.seats_booked *
            self.trip.price_per_seat
        )

    def __str__(self):
        return (
            f"{self.passenger.username} booked "
            f"{self.trip}"
        )


class Review(models.Model):
    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name="reviews",
    )

    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="submitted_reviews",
    )

    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ]
    )

    comment = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        default=timezone.now,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "-created_at",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "trip",
                    "reviewer",
                ],
                name="one_review_per_user_per_trip",
            ),
            models.CheckConstraint(
                check=models.Q(
                    rating__gte=1,
                    rating__lte=5,
                ),
                name="review_rating_between_one_and_five",
            ),
        ]

    def __str__(self):
        return (
            f"{self.reviewer.username}: "
            f"{self.rating}/5"
        )