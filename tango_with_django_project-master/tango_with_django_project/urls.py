from django.contrib import admin
from django.urls import path, include
from travel import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/register/", views.register, name="register"),
    path("", include("travel.urls")),  
]