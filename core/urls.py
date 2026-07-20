from django.urls import path
from django.contrib.auth import views as auth_views

from . import views


urlpatterns = [
    # Home
    path("", views.home, name="home"),

    # Authentication
    path("signup/", views.signup, name="signup",),
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login",),
    path("logout/", auth_views.LogoutView.as_view(), name="logout",),
    path("profile/", views.profile, name="profile",),
    path("password-change/", auth_views.PasswordChangeView.as_view(template_name="password_change.html", success_url="/profile/", ),name="password_change",),

    # Trips
    path("find/", views.find_rides, name="find_rides",),
    path("create/",views.create_trip, name="create_trip", ),
    path( "trip/<int:trip_id>/", views.trip_detail,name="trip_detail", ),
    path("trip/<int:trip_id>/edit/",views.edit_trip,name="edit_trip",),
    path("trip/<int:trip_id>/delete/",views.delete_trip, name="delete_trip",),
    path("trip/<int:trip_id>/passengers/", views.trip_passengers, name="trip_passengers",),

    # Bookings
    path("book/<int:trip_id>/",views.book_trip, name="book_trip",),
    path("my-bookings/",views.my_bookings,name="my_bookings",),
    path("cancel/<int:booking_id>/",views.cancel_booking,name="cancel_booking", ),

    # Driver dashboard
    path("dashboard/",views.driver_dashboard,name="dashboard",),

    # Reviews
    path("review/<int:trip_id>/",views.add_review,name="add_review", ),

    #admindashboard
    path("management/", views.admin_dashboard, name="admin_dashboard"),
    path("management/users/", views.manage_users, name="manage_users"),
    path("management/trips/", views.manage_trips, name="manage_trips"),
    path("management/bookings/", views.manage_bookings, name="manage_bookings"),
    path("management/reviews/", views.manage_reviews, name="manage_reviews"),

    path("logout/", auth_views.LogoutView.as_view(), name="logout",),

]