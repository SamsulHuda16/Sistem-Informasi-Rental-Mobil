from django.urls import path
from . import views

urlpatterns = [
    # Halaman depan publik (tanpa login)
    path("", views.landing_page, name="landing"),

    # Login khusus Admin & Petugas
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
]
