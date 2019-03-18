from django.conf.urls import url, include
from django.contrib.auth import views as auth_views

from apps.authentication import views

urlpatterns = [
    url(r"^login/$", auth_views.LoginView.as_view(), name="login"),
    url(r"^logout/$", views.logout_view, name="logout"),
    url(r"^oauth/", include("social_django.urls", namespace="social")),
]
