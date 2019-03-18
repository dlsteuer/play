from django.urls import path
from apps.ops import views


urlpatterns = [path("healthz/ready", views.ready), path("healthz/alive", views.alive)]
