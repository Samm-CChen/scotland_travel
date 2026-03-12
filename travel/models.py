from django.db import models
from django.contrib.auth.models import User

# City Model
class City(models.Model):
    name = models.CharField(max_length=100, verbose_name="City Name")
    description = models.TextField(blank=True, verbose_name="Description")
    cover_image = models.URLField(blank=True, verbose_name="Cover Image URL")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        verbose_name = "City"
        verbose_name_plural = "Cities"
        ordering = ['name']

    def __str__(self):
        return self.name  # CityName in list of backend


# Attraction Model
class Attraction(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="attractions", verbose_name="City")
    name = models.CharField(max_length=200, verbose_name="Attraction Name")
    description = models.TextField(blank=True, verbose_name="Description")
    official_url = models.URLField(blank=True, verbose_name="Official Website URL")
    cover_image = models.URLField(blank=True, verbose_name="Cover Image URL")

    class Meta:
        verbose_name = "Attraction"
        verbose_name_plural = "Attractions"
        ordering = ['city__name', 'name']
        # unique_together restriction
        unique_together = ['city', 'name']

    def __str__(self):
        return f"{self.city.name} - {self.name}"


# CityRating Model
class CityRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="city_ratings", verbose_name="User")
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="ratings", verbose_name="City")
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)], verbose_name="Rating")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        verbose_name = "City Rating"
        verbose_name_plural = "City Ratings"
        ordering = ['-created_at']
        # unique_together restriction
        unique_together = ['user', 'city']

    def __str__(self):
        return f"{self.user.username} - {self.city.name} ({self.rating} Stars)"


# AttractionRating Model
class AttractionRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="attraction_ratings", verbose_name="User")
    attraction = models.ForeignKey(Attraction, on_delete=models.CASCADE, related_name="ratings", verbose_name="Attraction")
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)], verbose_name="Rating")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        verbose_name = "Attraction Rating"
        verbose_name_plural = "Attraction Ratings"
        ordering = ['-created_at']
        # unique_together restriction
        unique_together = ['user', 'attraction']

    def __str__(self):
        return f"{self.user.username} - {self.attraction.name} ({self.rating} Stars)"


# Bookmark Model
class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookmarks", verbose_name="User")
    attraction = models.ForeignKey(Attraction, on_delete=models.CASCADE, related_name="bookmarks", verbose_name="Attraction")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        verbose_name = "Bookmark"
        verbose_name_plural = "Bookmarks"
        ordering = ['-created_at']
        # unique_together restriction
        unique_together = ['user', 'attraction']

    def __str__(self):
        return f"{self.user.username} - {self.attraction.name}"