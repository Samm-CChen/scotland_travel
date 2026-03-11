from django.urls import path
from . import views

urlpatterns = [
    path("cities/", views.city_list, name="city_list"),
    path("api/cities/<int:city_id>/", views.city_attractions, name="city_attractions"),
]