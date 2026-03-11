from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Avg
from .models import City, Attraction

# Create your views here.

def city_list(request):
    cities = City.objects.all()
    return render(request, "travel/city_list.html", {"cities": cities})


def city_attractions(request, city_id):
    city = get_object_or_404(City, id=city_id)

    attractions = (
        Attraction.objects
        .filter(city=city)
        .annotate(avg_rating=Avg('ratings_rating'))
        .order_by('-avg_rating')
        )
    
    data = []

    for a in attractions:
        data.append({
            "name": a.name,
            "image": a.image_url,
            "url": a.official_url,
            "rating": a.average_rating if a.average_rating else 0
        
        })

    return JsonResponse({"attractions": data})