# Import core Django modules
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Avg, Count
from django.views.generic import TemplateView
from django.db import IntegrityError

class BookmarkListView(TemplateView):
    template_name = 'travel/bookmarks.html'

    def get(self, request):
        from django.http import HttpResponse
        return HttpResponse("Bookmark Page")

# Import DRF modules
from rest_framework.response import Response
from rest_framework import status

from .models import City, Attraction, CityRating, AttractionRating, Bookmark
from .serializers import (
    CitySerializer,
    CityRatingSerializer,
    CityRatingStatsSerializer,
    AttractionRatingSerializer,
    AttractionRatingStatsSerializer,
    BookmarkSerializer,
    BookmarkListSerializer
)
from .forms import CityFilterForm

# Login required decorator for class-based views
login_required_mixin = method_decorator(login_required, name='dispatch')

# Core Page Views
class IndexView(View):
    """Homepage view - redirects to city list"""
    def get(self, request):
        return redirect('travel:cities')

class CityListView(View):
    """City list view with filtering support"""
    def get(self, request):
        # Initialize filter form
        form = CityFilterForm(request.GET)
        # Get filtered cities with rating stats
        if form.is_valid():
            cities = form.filter_cities()
        else:
            cities = City.objects.annotate(
                avg_rating=Avg('ratings__rating', default=0),
                rating_count=Count('ratings__rating', default=0)
            ).order_by('-avg_rating')

        # Serialize city data (for optional JSON response)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            serializer = CitySerializer(cities, many=True)
            return JsonResponse({'cities': serializer.data})

        # Render HTML template for normal requests
        context = {
            'cities': cities,
            'filter_form': form,
            'user': request.user
        }
        return render(request, 'travel/cities.html', context)

class CityDetailView(View):
    """City detail view with attraction list"""
    def get(self, request, city_id):
        city = get_object_or_404(City, id=city_id)
        attractions = Attraction.objects.filter(city=city).annotate(
            avg_rating=Avg('ratings__rating', default=0),
            rating_count=Count('ratings__rating', default=0)
        ).order_by('-avg_rating')

        # Get user's existing rating for the city (for UI state)
        user_rating = None
        if request.user.is_authenticated:
            user_rating = CityRating.objects.filter(user=request.user, city=city).first()

        context = {
            'city': city,
            'attractions': attractions,
            'user_rating': user_rating.rating if user_rating else 0,
            'user': request.user
        }
        return render(request, 'travel/city_detail.html', context)

class AttractionDetailView(View):
    """Attraction detail view with bookmark status"""
    def get(self, request, attraction_id):
        attraction = get_object_or_404(Attraction, id=attraction_id)

        # Get attraction stats
        stats = Attraction.objects.filter(id=attraction_id).annotate(
            avg_rating=Avg('ratings__rating', default=0),
            rating_count=Count('ratings__rating', default=0)
        ).first()

        # Check bookmark status for logged-in user
        is_bookmarked = False
        if request.user.is_authenticated:
            is_bookmarked = Bookmark.objects.filter(user=request.user, attraction=attraction).exists()

        context = {
            'attraction': attraction,
            'avg_rating': round(stats.avg_rating, 1) if stats.avg_rating else 0,
            'rating_count': stats.rating_count,
            'is_bookmarked': is_bookmarked,
            'user': request.user
        }
        return render(request, 'travel/attraction_detail.html', context)

class BookmarkListView(View):
    """User's bookmarked attractions list"""
    @login_required_mixin
    def get(self, request):
        bookmarks = Bookmark.objects.filter(user=request.user).select_related(
            'attraction', 'attraction__city'
        ).order_by('-created_at')

        # AJAX response (JSON) or HTML template
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            serializer = BookmarkListSerializer(bookmarks, many=True)
            return JsonResponse({'bookmarks': serializer.data})

        context = {
            'bookmarks': bookmarks,
            'user': request.user
        }
        return render(request, 'travel/bookmarks.html', context)

# AJAX API Views (Serializer Integrated)
class CityRatingSubmitView(View):
    """AJAX endpoint for submitting city ratings (serializer integrated)"""
    @login_required_mixin
    def post(self, request):
        # Initialize serializer with request data and user context
        serializer = CityRatingSerializer(data=request.POST, context={'request': request})

        if serializer.is_valid():
            # Save rating (prevents duplicates via update_or_create)
            serializer.save()

            # Calculate updated rating statistics
            city = serializer.validated_data['city']
            stats = city.ratings.aggregate(
                avg_rating=Avg('rating'),
                rating_count=Count('rating')
            )

            # Serialize statistics for response
            stats_data = {
                'avg_rating': round(stats['avg_rating'], 1) if stats['avg_rating'] else 0,
                'rating_count': stats['rating_count'],
                'status': 'success',
                'message': 'Rating submitted successfully'
            }
            stats_serializer = CityRatingStatsSerializer(stats_data)

            return JsonResponse(stats_serializer.data, status=200)

        # Return validation errors
        return JsonResponse({
            'status': 'error',
            'errors': serializer.errors,
            'message': 'Failed to submit rating'
        }, status=400)

class AttractionRatingSubmitView(View):
    """AJAX endpoint for submitting attraction ratings"""
    @login_required_mixin
    def post(self, request):
        serializer = AttractionRatingSerializer(data=request.POST, context={'request': request})

        if serializer.is_valid():
            serializer.save()

            # Calculate updated stats
            attraction = serializer.validated_data['attraction']
            stats = attraction.ratings.aggregate(
                avg_rating=Avg('rating'),
                rating_count=Count('rating')
            )

            # Serialize stats response
            stats_data = {
                'avg_rating': round(stats['avg_rating'], 1) if stats['avg_rating'] else 0,
                'rating_count': stats['rating_count'],
                'status': 'success',
                'message': 'Attraction rating submitted successfully'
            }
            stats_serializer = AttractionRatingStatsSerializer(stats_data)

            return JsonResponse(stats_serializer.data, status=200)

        return JsonResponse({
            'status': 'error',
            'errors': serializer.errors,
            'message': 'Failed to submit attraction rating'
        }, status=400)

class BookmarkToggleView(View):
    """AJAX endpoint for toggling attraction bookmarks"""
    @login_required_mixin
    def post(self, request):
        serializer = BookmarkSerializer(data=request.POST, context={'request': request})

        if serializer.is_valid():
            # Toggle bookmark (add/remove)
            result = serializer.save()

            return JsonResponse({
                'status': result.get('status', 'success'),
                'message': result.get('message', 'Bookmark updated successfully'),
                'attraction_id': request.POST.get('attraction')
            }, status=200)

        return JsonResponse({
            'status': 'error',
            'errors': serializer.errors,
            'message': 'Failed to update bookmark'
        }, status=400)

class CityFilterView(View):
    """AJAX endpoint for city filtering"""
    def get(self, request):
        form = CityFilterForm(request.GET)
        if form.is_valid():
            cities = form.filter_cities()
            serializer = CitySerializer(cities, many=True)
            return JsonResponse({'cities': serializer.data})

        return JsonResponse({
            'status': 'error',
            'errors': form.errors,
            'message': 'Filter validation failed'
        }, status=400)