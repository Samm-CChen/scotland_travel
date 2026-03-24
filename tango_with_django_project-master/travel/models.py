from django.db import models
from django.contrib.auth.models import User


class City(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Attraction(models.Model):
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name="attractions"
    )
    name = models.CharField(max_length=200)
    description = models.TextField()
    official_url = models.URLField()

    def __str__(self):
        return self.name


class Bookmark(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bookmarks"
    )
    attraction = models.ForeignKey(
        Attraction,
        on_delete=models.CASCADE,
        related_name="bookmarked_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "attraction")

    def __str__(self):
        return f"{self.user.username} -> {self.attraction.name}"