from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Booking, Review, Trip


# Remove Django's default User admin so we can customize it.
admin.site.unregister(User)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "date_joined",
        "last_login",
    )

    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
    )

    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
    )

    ordering = (
        "-date_joined",
    )

    readonly_fields = (
        "date_joined",
        "last_login",
    )


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "route",
        "driver",
        "date",
        "time",
        "seats_available",
        "price_per_seat",
    )

    list_filter = (
        "date",
        "driver",
    )

    search_fields = (
        "start_location",
        "end_location",
        "driver__username",
        "driver__email",
    )

    ordering = (
        "-date",
        "-time",
    )

    list_select_related = (
        "driver",
    )

    @admin.display(description="Route")
    def route(self, obj):
        return (
            f"{obj.start_location} → "
            f"{obj.end_location}"
        )


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "passenger",
        "route",
        "driver",
        "seats_booked",
        "booking_value",
    )

    list_filter = (
        "trip__date",
        "trip__driver",
    )

    search_fields = (
        "passenger__username",
        "passenger__email",
        "trip__driver__username",
        "trip__start_location",
        "trip__end_location",
    )

    list_select_related = (
        "passenger",
        "trip",
        "trip__driver",
    )

    @admin.display(description="Route")
    def route(self, obj):
        return (
            f"{obj.trip.start_location} → "
            f"{obj.trip.end_location}"
        )

    @admin.display(description="Driver")
    def driver(self, obj):
        return obj.trip.driver

    @admin.display(description="Booking value")
    def booking_value(self, obj):
        value = (
            obj.seats_booked *
            obj.trip.price_per_seat
        )

        return f"${value:.2f}"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "reviewer",
        "route",
        "driver",
        "rating",
        "short_comment",
    )

    list_filter = (
        "rating",
        "trip__driver",
    )

    search_fields = (
        "reviewer__username",
        "reviewer__email",
        "trip__driver__username",
        "trip__start_location",
        "trip__end_location",
        "comment",
    )

    list_select_related = (
        "reviewer",
        "trip",
        "trip__driver",
    )

    @admin.display(description="Route")
    def route(self, obj):
        return (
            f"{obj.trip.start_location} → "
            f"{obj.trip.end_location}"
        )

    @admin.display(description="Driver")
    def driver(self, obj):
        return obj.trip.driver

    @admin.display(description="Comment")
    def short_comment(self, obj):
        if not obj.comment:
            return "No comment"

        if len(obj.comment) <= 60:
            return obj.comment

        return f"{obj.comment[:60]}..."