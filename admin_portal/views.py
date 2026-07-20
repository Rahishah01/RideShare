from django.shortcuts import render
from django.core.paginator import Paginator
from decimal import Decimal
from datetime import datetime
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import (
    Avg,
    Count,
    DecimalField,
    ExpressionWrapper,
    F,
    IntegerField,
    OuterRef,
    Q,
    Subquery,
    Sum,
    Value,
)
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from core.models import Booking, Review, Trip
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, render
from django.utils import timezone


User = get_user_model()



@staff_member_required
def dashboard(request):
    booking_value_expression = ExpressionWrapper(
        F("seats_booked") * F("trip__price_per_seat"),
        output_field=DecimalField(
            max_digits=12,
            decimal_places=2,
        ),
    )

    booking_summary = Booking.objects.aggregate(
        total_seats=Sum("seats_booked"),
        gross_revenue=Sum(booking_value_expression),
    )

    gross_revenue = (
        booking_summary["gross_revenue"]
        or Decimal("0.00")
    )

    total_seats = (
        booking_summary["total_seats"]
        or 0
    )

    platform_fee = (
        gross_revenue *
        Decimal("0.10")
    )

    driver_income = (
        gross_revenue -
        platform_fee
    )

    average_rating = Review.objects.aggregate(
        average=Avg("rating")
    )["average"] or 0

    recent_users = User.objects.order_by(
        "-date_joined"
    )[:5]

    recent_trips = Trip.objects.select_related(
        "driver"
    ).order_by("-id")[:5]

    recent_bookings = Booking.objects.select_related(
        "passenger",
        "trip",
        "trip__driver",
    ).order_by("-id")[:5]

    popular_routes = Trip.objects.values(
        "start_location",
        "end_location",
    ).annotate(
        trip_count=Count("id"),
        booking_count=Count(
            "bookings",
            distinct=True,
        ),
    ).order_by(
        "-booking_count",
        "-trip_count",
    )[:5]

    top_drivers = User.objects.annotate(
        trips_offered=Count(
            "offered_trips",
            distinct=True,
        ),
        driver_rating=Avg(
            "offered_trips__reviews__rating"
        ),
        passengers_served=Count(
            "offered_trips__bookings__passenger",
            distinct=True,
        ),
    ).filter(
        trips_offered__gt=0
    ).order_by(
        "-driver_rating",
        "-trips_offered",
    )[:5]

    context = {
        "total_users": User.objects.count(),
        "total_trips": Trip.objects.count(),
        "total_bookings": Booking.objects.count(),
        "total_reviews": Review.objects.count(),

        "total_seats": total_seats,
        "gross_revenue": gross_revenue,
        "platform_fee": platform_fee,
        "driver_income": driver_income,
        "average_rating": average_rating,

        "recent_users": recent_users,
        "recent_trips": recent_trips,
        "recent_bookings": recent_bookings,
        "popular_routes": popular_routes,
        "top_drivers": top_drivers,
    }

    return render(
        request,
        "admin_portal/dashboard.html",
        context,
    )

@staff_member_required
def users(request):
    all_users = User.objects.annotate(
        trips_offered=Count(
            "offered_trips",
            distinct=True,
        ),
        bookings_made=Count(
            "ride_bookings",
            distinct=True,
        ),
    ).order_by("-date_joined")

    return render(
        request,
        "admin_portal/users.html",
        {
            "users": all_users,
        },
    )


@staff_member_required
def trips(request):
    all_trips = Trip.objects.select_related(
        "driver"
    ).annotate(
        booking_count=Count(
            "bookings",
            distinct=True,
        ),
        review_count=Count(
            "reviews",
            distinct=True,
        ),
    ).order_by("-id")

    return render(
        request,
        "admin_portal/trips.html",
        {
            "trips": all_trips,
        },
    )


@staff_member_required
def bookings(request):
    search_query = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "all")
    sort_option = request.GET.get("sort", "newest")

    booking_value_expression = ExpressionWrapper(
        F("seats_booked")
        * F("trip__price_per_seat"),
        output_field=DecimalField(
            max_digits=12,
            decimal_places=2,
        ),
    )

    bookings_queryset = (
        Booking.objects
        .select_related(
            "passenger",
            "trip",
            "trip__driver",
        )
        .annotate(
            booking_value=booking_value_expression,
        )
    )

    if search_query:
        bookings_queryset = bookings_queryset.filter(
            Q(passenger__username__icontains=search_query)
            | Q(passenger__email__icontains=search_query)
            | Q(passenger__first_name__icontains=search_query)
            | Q(passenger__last_name__icontains=search_query)
            | Q(trip__driver__username__icontains=search_query)
            | Q(trip__driver__email__icontains=search_query)
            | Q(trip__start_location__icontains=search_query)
            | Q(trip__end_location__icontains=search_query)
        )

    today = timezone.localdate()

    if status_filter == "upcoming":
        bookings_queryset = bookings_queryset.filter(
            trip__date__gt=today,
        )

    elif status_filter == "today":
        bookings_queryset = bookings_queryset.filter(
            trip__date=today,
        )

    elif status_filter == "completed":
        bookings_queryset = bookings_queryset.filter(
            trip__date__lt=today,
        )

    elif status_filter == "unscheduled":
        bookings_queryset = bookings_queryset.filter(
            trip__date__isnull=True,
        )

    sort_options = {
        "newest": "-id",
        "oldest": "id",
        "highest_value": "-booking_value",
        "most_seats": "-seats_booked",
        "departure": "trip__date",
    }

    bookings_queryset = bookings_queryset.order_by(
        sort_options.get(
            sort_option,
            "-id",
        )
    )

    paginator = Paginator(
        bookings_queryset,
        12,
    )

    bookings_page = paginator.get_page(
        request.GET.get("page")
    )

    for booking in bookings_page:
        trip_date = booking.trip.date

        if trip_date is None:
            booking.operation_status = "unscheduled"

        elif trip_date < today:
            booking.operation_status = "completed"

        elif trip_date == today:
            booking.operation_status = "today"

        else:
            booking.operation_status = "upcoming"

    booking_summary = Booking.objects.aggregate(
        total_seats=Coalesce(
            Sum("seats_booked"),
            Value(
                0,
                output_field=IntegerField(),
            ),
        ),
        total_revenue=Coalesce(
            Sum(
                ExpressionWrapper(
                    F("seats_booked")
                    * F("trip__price_per_seat"),
                    output_field=DecimalField(
                        max_digits=12,
                        decimal_places=2,
                    ),
                )
            ),
            Value(
                Decimal("0.00"),
                output_field=DecimalField(
                    max_digits=12,
                    decimal_places=2,
                ),
            ),
        ),
    )

    context = {
        "bookings_page": bookings_page,

        "search_query": search_query,
        "status_filter": status_filter,
        "sort_option": sort_option,

        "total_bookings": Booking.objects.count(),
        "total_seats": booking_summary["total_seats"],
        "total_revenue": booking_summary["total_revenue"],

        "upcoming_bookings": Booking.objects.filter(
            trip__date__gte=today,
        ).count(),

        "completed_bookings": Booking.objects.filter(
            trip__date__lt=today,
        ).count(),
    }

    return render(
        request,
        "admin_portal/bookings.html",
        context,
    )


@staff_member_required
def reviews(request):
    search_query = request.GET.get("q", "").strip()
    rating_filter = request.GET.get("rating", "all")
    sort_option = request.GET.get("sort", "newest")

    reviews_queryset = (
        Review.objects
        .select_related(
            "reviewer",
            "trip",
            "trip__driver",
        )
    )

    if search_query:
        reviews_queryset = reviews_queryset.filter(
            Q(reviewer__username__icontains=search_query)
            | Q(reviewer__email__icontains=search_query)
            | Q(reviewer__first_name__icontains=search_query)
            | Q(reviewer__last_name__icontains=search_query)
            | Q(trip__driver__username__icontains=search_query)
            | Q(trip__driver__email__icontains=search_query)
            | Q(trip__start_location__icontains=search_query)
            | Q(trip__end_location__icontains=search_query)
            | Q(comment__icontains=search_query)
        )

    if rating_filter in {"1", "2", "3", "4", "5"}:
        reviews_queryset = reviews_queryset.filter(
            rating=int(rating_filter)
        )

    sort_options = {
        "newest": "-id",
        "oldest": "id",
        "highest": "-rating",
        "lowest": "rating",
        "reviewer": "reviewer__username",
        "driver": "trip__driver__username",
    }

    reviews_queryset = reviews_queryset.order_by(
        sort_options.get(
            sort_option,
            "-id",
        ),
        "-id",
    )

    paginator = Paginator(
        reviews_queryset,
        12,
    )

    reviews_page = paginator.get_page(
        request.GET.get("page")
    )

    review_summary = Review.objects.aggregate(
        average_rating=Avg("rating"),
        five_star_count=Count(
            "id",
            filter=Q(rating=5),
        ),
        one_star_count=Count(
            "id",
            filter=Q(rating=1),
        ),
    )

    context = {
        "reviews_page": reviews_page,

        "search_query": search_query,
        "rating_filter": rating_filter,
        "sort_option": sort_option,

        "total_reviews": Review.objects.count(),

        "average_rating": (
            review_summary["average_rating"]
            or 0
        ),

        "five_star_reviews": (
            review_summary["five_star_count"]
            or 0
        ),

        "one_star_reviews": (
            review_summary["one_star_count"]
            or 0
        ),

        "reviewed_drivers": (
            Review.objects
            .values("trip__driver")
            .distinct()
            .count()
        ),
    }

    return render(
        request,
        "admin_portal/reviews.html",
        context,
    )




@staff_member_required
def users(request):
    search_query = request.GET.get("q", "").strip()
    role_filter = request.GET.get("role", "all")
    status_filter = request.GET.get("status", "all")
    sort_option = request.GET.get("sort", "newest")

    trip_count_subquery = (
        Trip.objects
        .filter(driver=OuterRef("pk"))
        .values("driver")
        .annotate(total=Count("id"))
        .values("total")[:1]
    )

    booking_count_subquery = (
        Booking.objects
        .filter(passenger=OuterRef("pk"))
        .values("passenger")
        .annotate(total=Count("id"))
        .values("total")[:1]
    )

    seats_booked_subquery = (
        Booking.objects
        .filter(passenger=OuterRef("pk"))
        .values("passenger")
        .annotate(total=Sum("seats_booked"))
        .values("total")[:1]
    )

    driver_rating_subquery = (
        Review.objects
        .filter(trip__driver=OuterRef("pk"))
        .values("trip__driver")
        .annotate(average=Avg("rating"))
        .values("average")[:1]
    )

    users_queryset = User.objects.annotate(
        trips_offered=Coalesce(
            Subquery(
                trip_count_subquery,
                output_field=IntegerField(),
            ),
            Value(0),
        ),
        bookings_made=Coalesce(
            Subquery(
                booking_count_subquery,
                output_field=IntegerField(),
            ),
            Value(0),
        ),
        seats_reserved=Coalesce(
            Subquery(
                seats_booked_subquery,
                output_field=IntegerField(),
            ),
            Value(0),
        ),
        average_driver_rating=Coalesce(
            Subquery(
                driver_rating_subquery,
                output_field=DecimalField(
                    max_digits=4,
                    decimal_places=2,
                ),
            ),
            Value(
                0,
                output_field=DecimalField(
                    max_digits=4,
                    decimal_places=2,
                ),
            ),
        ),
    )

    if search_query:
        users_queryset = users_queryset.filter(
            Q(username__icontains=search_query)
            | Q(email__icontains=search_query)
            | Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
        )

    if role_filter == "superuser":
        users_queryset = users_queryset.filter(
            is_superuser=True,
        )

    elif role_filter == "staff":
        users_queryset = users_queryset.filter(
            is_staff=True,
            is_superuser=False,
        )

    elif role_filter == "drivers":
        users_queryset = users_queryset.filter(
            trips_offered__gt=0,
        )

    elif role_filter == "passengers":
        users_queryset = users_queryset.filter(
            bookings_made__gt=0,
        )

    elif role_filter == "regular":
        users_queryset = users_queryset.filter(
            is_staff=False,
            is_superuser=False,
        )

    if status_filter == "active":
        users_queryset = users_queryset.filter(
            is_active=True,
        )

    elif status_filter == "inactive":
        users_queryset = users_queryset.filter(
            is_active=False,
        )

    sort_options = {
        "newest": "-date_joined",
        "oldest": "date_joined",
        "username": "username",
        "most_trips": "-trips_offered",
        "most_bookings": "-bookings_made",
        "highest_rated": "-average_driver_rating",
    }

    users_queryset = users_queryset.order_by(
        sort_options.get(
            sort_option,
            "-date_joined",
        ),
        "username",
    )

    paginator = Paginator(
        users_queryset,
        10,
    )

    page_number = request.GET.get("page")
    users_page = paginator.get_page(page_number)

    all_users = User.objects.all()

    context = {
        "users_page": users_page,
        "search_query": search_query,
        "role_filter": role_filter,
        "status_filter": status_filter,
        "sort_option": sort_option,

        "total_users": all_users.count(),
        "active_users": all_users.filter(
            is_active=True,
        ).count(),
        "staff_users": all_users.filter(
            is_staff=True,
        ).count(),
        "driver_users": User.objects.filter(
            id__in=Trip.objects.values("driver_id")
        ).count(),
    }

    return render(
        request,
        "admin_portal/users.html",
        context,
    )

@staff_member_required
def user_detail(request, user_id):
    platform_user = get_object_or_404(
        User,
        pk=user_id,
    )

    booking_value_expression = ExpressionWrapper(
        F("seats_booked") * F("trip__price_per_seat"),
        output_field=DecimalField(
            max_digits=12,
            decimal_places=2,
        ),
    )

    offered_trips = (
        Trip.objects
        .filter(driver=platform_user)
        .order_by("-id")
    )

    passenger_bookings = (
        Booking.objects
        .filter(passenger=platform_user)
        .select_related(
            "trip",
            "trip__driver",
        )
        .annotate(
            booking_value=booking_value_expression,
        )
        .order_by("-id")
    )

    received_bookings = (
        Booking.objects
        .filter(trip__driver=platform_user)
        .select_related(
            "passenger",
            "trip",
        )
        .annotate(
            booking_value=booking_value_expression,
        )
        .order_by("-id")
    )

    driver_reviews = (
        Review.objects
        .filter(trip__driver=platform_user)
        .select_related("trip")
        .order_by("-id")
    )

    passenger_summary = passenger_bookings.aggregate(
        total_seats=Sum("seats_booked"),
        total_spent=Sum(booking_value_expression),
    )

    driver_summary = received_bookings.aggregate(
        passengers_served=Count(
            "passenger",
            distinct=True,
        ),
        seats_sold=Sum("seats_booked"),
        gross_revenue=Sum(booking_value_expression),
    )

    average_rating = driver_reviews.aggregate(
        average=Avg("rating"),
    )["average"] or 0

    total_spent = (
        passenger_summary["total_spent"]
        or Decimal("0.00")
    )

    gross_revenue = (
        driver_summary["gross_revenue"]
        or Decimal("0.00")
    )

    platform_commission = (
        gross_revenue * Decimal("0.10")
    )

    driver_earnings = (
        gross_revenue - platform_commission
    )

    context = {
        "platform_user": platform_user,

        "offered_trips": offered_trips[:10],
        "passenger_bookings": passenger_bookings[:10],
        "received_bookings": received_bookings[:10],
        "driver_reviews": driver_reviews[:10],

        "trips_offered_count": offered_trips.count(),
        "bookings_made_count": passenger_bookings.count(),
        "bookings_received_count": received_bookings.count(),
        "reviews_received_count": driver_reviews.count(),

        "seats_reserved": (
            passenger_summary["total_seats"]
            or 0
        ),
        "total_spent": total_spent,

        "passengers_served": (
            driver_summary["passengers_served"]
            or 0
        ),
        "seats_sold": (
            driver_summary["seats_sold"]
            or 0
        ),

        "gross_revenue": gross_revenue,
        "platform_commission": platform_commission,
        "driver_earnings": driver_earnings,
        "average_rating": average_rating,
    }

    return render(
        request,
        "admin_portal/user_detail.html",
        context,
    )


@staff_member_required
def trips(request):
    search_query = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "all")
    occupancy_filter = request.GET.get("occupancy", "all")
    sort_option = request.GET.get("sort", "newest")

    booking_value_expression = ExpressionWrapper(
        F("bookings__seats_booked")
        * F("price_per_seat"),
        output_field=DecimalField(
            max_digits=12,
            decimal_places=2,
        ),
    )

    trips_queryset = (
        Trip.objects
        .select_related("driver")
        .annotate(
            booked_seats=Coalesce(
                Sum("bookings__seats_booked"),
                Value(
                    0,
                    output_field=IntegerField(),
                ),
            ),
            booking_count=Count(
                "bookings",
                distinct=True,
            ),
            passenger_count=Count(
                "bookings__passenger",
                distinct=True,
            ),
            gross_revenue=Coalesce(
                Sum(booking_value_expression),
                Value(
                    Decimal("0.00"),
                    output_field=DecimalField(
                        max_digits=12,
                        decimal_places=2,
                    ),
                ),
            ),
        )
    )

    if search_query:
        trips_queryset = trips_queryset.filter(
            Q(start_location__icontains=search_query)
            | Q(end_location__icontains=search_query)
            | Q(driver__username__icontains=search_query)
            | Q(driver__email__icontains=search_query)
            | Q(driver__first_name__icontains=search_query)
            | Q(driver__last_name__icontains=search_query)
        )

    today = timezone.localdate()

    if status_filter == "upcoming":
        trips_queryset = trips_queryset.filter(
            date__gt=today,
        )

    elif status_filter == "today":
        trips_queryset = trips_queryset.filter(
            date=today,
        )

    elif status_filter == "completed":
        trips_queryset = trips_queryset.filter(
            date__lt=today,
        )

    elif status_filter == "available":
        trips_queryset = trips_queryset.filter(
            date__gte=today,
            seats_available__gt=0,
        )

    elif status_filter == "full":
        trips_queryset = trips_queryset.filter(
            date__gte=today,
            seats_available=0,
        )

    if occupancy_filter == "empty":
        trips_queryset = trips_queryset.filter(
            booked_seats=0,
        )

    elif occupancy_filter == "low":
        trips_queryset = trips_queryset.filter(
            booked_seats__gt=0,
        ).exclude(
            seats_available=0,
        )

    elif occupancy_filter == "full":
        trips_queryset = trips_queryset.filter(
            seats_available=0,
        )

    sort_options = {
        "newest": "-id",
        "oldest": "id",
        "departure": "date",
        "highest_revenue": "-gross_revenue",
        "most_booked": "-booked_seats",
        "price_high": "-price_per_seat",
        "price_low": "price_per_seat",
    }

    trips_queryset = trips_queryset.order_by(
        sort_options.get(
            sort_option,
            "-id",
        )
    )

    # Add display-only calculations to every trip.
    for trip in trips_queryset:
        trip.total_capacity = (
            trip.seats_available
            + trip.booked_seats
        )

        if trip.total_capacity > 0:
            trip.occupancy_percentage = round(
                (
                    trip.booked_seats
                    / trip.total_capacity
                ) * 100
            )
        else:
            trip.occupancy_percentage = 0

        trip.platform_commission = (
            trip.gross_revenue
            * Decimal("0.10")
        )

        trip.driver_earnings = (
            trip.gross_revenue
            - trip.platform_commission
        )

        if trip.date is None:
            trip.operation_status = "unscheduled"

        elif trip.date < today:
            trip.operation_status = "completed"

        elif trip.date == today:
            trip.operation_status = "today"

        elif trip.seats_available == 0:
            trip.operation_status = "full"

        else:
            trip.operation_status = "upcoming"

    paginator = Paginator(
        trips_queryset,
        10,
    )

    trips_page = paginator.get_page(
        request.GET.get("page")
    )

    all_trips = Trip.objects.annotate(
        booked_seats=Coalesce(
            Sum("bookings__seats_booked"),
            Value(
                0,
                output_field=IntegerField(),
            ),
        ),
        gross_revenue=Coalesce(
            Sum(
                ExpressionWrapper(
                    F("bookings__seats_booked")
                    * F("price_per_seat"),
                    output_field=DecimalField(
                        max_digits=12,
                        decimal_places=2,
                    ),
                )
            ),
            Value(
                Decimal("0.00"),
                output_field=DecimalField(
                    max_digits=12,
                    decimal_places=2,
                ),
            ),
        ),
    )

    summary = all_trips.aggregate(
        seats_sold=Coalesce(
            Sum("booked_seats"),
            Value(0),
        ),
        total_revenue=Coalesce(
            Sum("gross_revenue"),
            Value(
                Decimal("0.00"),
                output_field=DecimalField(
                    max_digits=12,
                    decimal_places=2,
                ),
            ),
        ),
    )

    context = {
        "trips_page": trips_page,

        "search_query": search_query,
        "status_filter": status_filter,
        "occupancy_filter": occupancy_filter,
        "sort_option": sort_option,

        "total_trips": all_trips.count(),
        "upcoming_trips": all_trips.filter(
            date__gte=today,
        ).count(),
        "full_trips": all_trips.filter(
            date__gte=today,
            seats_available=0,
        ).count(),
        "seats_sold": summary["seats_sold"],
        "total_revenue": summary["total_revenue"],
    }

    return render(
        request,
        "admin_portal/trips.html",
        context,
    )

@staff_member_required
def trip_detail(request, trip_id):
    trip = get_object_or_404(
        Trip.objects.select_related("driver"),
        pk=trip_id,
    )

    booking_value_expression = ExpressionWrapper(
        F("seats_booked")
        * F("trip__price_per_seat"),
        output_field=DecimalField(
            max_digits=12,
            decimal_places=2,
        ),
    )

    trip_bookings = (
        Booking.objects
        .filter(trip=trip)
        .select_related("passenger")
        .annotate(
            booking_value=booking_value_expression,
        )
        .order_by("-id")
    )

    trip_reviews = (
        Review.objects
        .filter(trip=trip)
        .select_related("reviewer")
        .order_by("-id")
    )

    booking_summary = trip_bookings.aggregate(
        seats_sold=Coalesce(
            Sum("seats_booked"),
            Value(
                0,
                output_field=IntegerField(),
            ),
        ),
        passenger_count=Count(
            "passenger",
            distinct=True,
        ),
        gross_revenue=Coalesce(
            Sum(booking_value_expression),
            Value(
                Decimal("0.00"),
                output_field=DecimalField(
                    max_digits=12,
                    decimal_places=2,
                ),
            ),
        ),
    )

    driver_trip_count = Trip.objects.filter(
        driver=trip.driver,
    ).count()

    driver_average_rating = (
        Review.objects
        .filter(trip__driver=trip.driver)
        .aggregate(
            average=Avg("rating")
        )["average"]
        or 0
    )

    trip_average_rating = (
        trip_reviews.aggregate(
            average=Avg("rating")
        )["average"]
        or 0
    )

    seats_sold = booking_summary["seats_sold"] or 0
    seats_available = trip.seats_available or 0

    total_capacity = (
        seats_sold
        + seats_available
    )

    if total_capacity > 0:
        occupancy_percentage = round(
            (
                seats_sold
                / total_capacity
            )
            * 100
        )
    else:
        occupancy_percentage = 0

    gross_revenue = (
        booking_summary["gross_revenue"]
        or Decimal("0.00")
    )

    platform_commission = (
        gross_revenue
        * Decimal("0.10")
    )

    driver_earnings = (
        gross_revenue
        - platform_commission
    )

    today = timezone.localdate()

    if trip.date is None:
        operation_status = "unscheduled"

    elif trip.date < today:
        operation_status = "completed"

    elif trip.date == today:
        operation_status = "today"

    elif seats_available == 0:
        operation_status = "full"

    else:
        operation_status = "upcoming"

    context = {
        "trip": trip,
        "trip_bookings": trip_bookings,
        "trip_reviews": trip_reviews,

        "seats_sold": seats_sold,
        "seats_available": seats_available,
        "total_capacity": total_capacity,
        "occupancy_percentage": occupancy_percentage,

        "passenger_count":
            booking_summary["passenger_count"]
            or 0,

        "gross_revenue": gross_revenue,
        "platform_commission": platform_commission,
        "driver_earnings": driver_earnings,

        "driver_trip_count": driver_trip_count,
        "driver_average_rating":
            driver_average_rating,

        "trip_average_rating":
            trip_average_rating,

        "operation_status":
            operation_status,
    }

    return render(
        request,
        "admin_portal/trip_detail.html",
        context,
    )

@staff_member_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related(
            "passenger",
            "trip",
            "trip__driver",
        ),
        pk=booking_id,
    )

    seats_booked = booking.seats_booked or 0
    price_per_seat = (
        booking.trip.price_per_seat
        or Decimal("0.00")
    )

    booking_value = (
        Decimal(seats_booked)
        * price_per_seat
    )

    platform_commission = (
        booking_value
        * Decimal("0.10")
    )

    driver_earnings = (
        booking_value
        - platform_commission
    )

    today = timezone.localdate()
    trip_date = booking.trip.date

    if trip_date is None:
        operation_status = "unscheduled"

    elif trip_date < today:
        operation_status = "completed"

    elif trip_date == today:
        operation_status = "today"

    else:
        operation_status = "upcoming"

    passenger_booking_count = (
        Booking.objects
        .filter(
            passenger=booking.passenger
        )
        .count()
    )

    passenger_seats_reserved = (
        Booking.objects
        .filter(
            passenger=booking.passenger
        )
        .aggregate(
            total=Coalesce(
                Sum("seats_booked"),
                Value(
                    0,
                    output_field=IntegerField(),
                ),
            )
        )["total"]
    )

    driver_trip_count = (
        Trip.objects
        .filter(
            driver=booking.trip.driver
        )
        .count()
    )

    driver_average_rating = (
        Review.objects
        .filter(
            trip__driver=booking.trip.driver
        )
        .aggregate(
            average=Avg("rating")
        )["average"]
        or 0
    )

    context = {
        "booking": booking,

        "booking_value": booking_value,
        "platform_commission":
            platform_commission,
        "driver_earnings":
            driver_earnings,

        "operation_status":
            operation_status,

        "passenger_booking_count":
            passenger_booking_count,
        "passenger_seats_reserved":
            passenger_seats_reserved,

        "driver_trip_count":
            driver_trip_count,
        "driver_average_rating":
            driver_average_rating,
    }

    return render(
        request,
        "admin_portal/booking_detail.html",
        context,
    )
