from django.urls import path
from . import views

# Define namespace for URL reversing (matches project-level urls.py)
app_name = 'travel'

urlpatterns = [
    # Core page routes
    path('index/', views.IndexView.as_view(), name='index'),
    path('cities/', views.CityListView.as_view(), name='cities'),
    path('city/<int:city_id>/', views.CityDetailView.as_view(), name='city_detail'),
    path('attraction/<int:attraction_id>/', views.AttractionDetailView.as_view(), name='attraction_detail'),
    path('bookmarks/', views.BookmarkListView.as_view(), name='bookmarks'),

    # AJAX API routes (for JavaScript interactions)
    path('api/city/rating/submit/', views.CityRatingSubmitView.as_view(), name='city_rating_submit'),
    path('api/attraction/rating/submit/', views.AttractionRatingSubmitView.as_view(), name='attraction_rating_submit'),
    path('api/attraction/bookmark/toggle/', views.BookmarkToggleView.as_view(), name='bookmark_toggle'),
    path('api/cities/filter/', views.CityFilterView.as_view(), name='city_filter'),

]