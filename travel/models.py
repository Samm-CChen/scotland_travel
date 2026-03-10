from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg

# Create your models here.

class City(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    

class Attraction(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    image_url = models.URLField(blank=True)
    official_url = models.URLField(blank=True)

    def average_rating(self):
        avg = self.ratings.aggregate(Avg('rating'))['ratring_avg']
        return avg if avg else 0
    
    def __str__(self):
        return self.name
    

class AttractionRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    attraction = models.ForeignKey(Attraction, on_delete=models.CASCADE, related_name="ratings")
    rating = models.IntegerField()
