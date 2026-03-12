from django.urls import path
from . import views

urlpatterns = [
    path("cities/", views.city_list, name="city_list"),
    path("api/cities/<int:city_id>/", views.city_attractions, name="city_attractions"),
    path("attraction/<int:attraction_id>/", views.attraction_detail, name="attraction_detail"),
]