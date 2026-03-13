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

    min_rating = request.GET.get("min_rating")

    attractions = (
        Attraction.objects
        .filter(city=city)
        .annotate(avg_rating=Avg('ratings__rating'))
        .order_by('-avg_rating')
        )
    

    if min_rating:
        try:
            min_rating =float(min_rating)
            attraction = attraction.filter(avg_rating__gte=min_rating)
        except ValueError:
            pass
    
    data = []

    for a in attractions:
        data.append({
            "id":a.id,
            "name": a.name,
            "image": a.image_url,
            "url": a.official_url,
            "rating": a.avg_rating if a.avg_rating else 0,
        
        })

    return JsonResponse({"attractions": data})


def attraction_detail(request, attraction_id):
    attraction = get_object_or_404(Attraction, id=attraction_id)
    return render(request,'travel/attraction_detail.html', {'attraction': attraction})