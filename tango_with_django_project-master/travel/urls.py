from django.urls import path
from . import views

app_name = "travel"

urlpatterns = [
    path("", views.home, name="home"),
    path("cities/", views.cities, name="cities"),
    path("protected/", views.protected, name="protected"),
    # Attraction details
    path("attractions/<int:attraction_id>/", views.attraction_detail, name="attraction_detail"),
    # Bookmark switch
    path("attractions/<int:attraction_id>/bookmark/", views.toggle_bookmark, name="toggle_bookmark"),
    # Bookmark list
    path("bookmarks/", views.bookmarks, name="bookmarks"),
]