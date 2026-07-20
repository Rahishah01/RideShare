from django.urls import path

from . import views


app_name = "admin_portal"


urlpatterns = [
    path("",views.dashboard, name="dashboard", ),
    path("users/", views.users, name="users",),
    path("trips/", views.trips, name="trips",),
    path("bookings/", views.bookings, name="bookings",),
    path( "reviews/", views.reviews, name="reviews",),
    path("users/<int:user_id>/", views.user_detail, name="user_detail",),
    path("trips/<int:trip_id>/", views.trip_detail, name="trip_detail",),
    path("bookings/<int:booking_id>/", views.booking_detail, name="booking_detail",),
    
]