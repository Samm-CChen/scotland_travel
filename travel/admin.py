# Import core admin modules and utilities
from django.contrib import admin
from django.http import HttpResponse
import csv
from django.utils.html import format_html

# Import all models from travel application
from .models import (
    City,               # City Models
    Attraction,         # Attraction Models
    CityRating,         # CityRating Models
    AttractionRating,   # AttractionRating Models
    Bookmark            # Bookmark Models
)

# Universal Utility Functions
def export_as_csv(modeladmin, request, queryset):
    """Custom action: Export selected data to CSV file"""
    meta = modeladmin.model._meta
    field_names = [field.name for field in meta.fields]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={meta.verbose_name_plural}.csv'
    writer = csv.writer(response)

    writer.writerow(field_names)
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in field_names])

    return response
export_as_csv.short_description = "Export selected data as CSV file"

# 1. CityAdmin
@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    """
    City model backend management configuration class
    Function: Customize display, search, filtering, sorting rules of city data + rating statistics
    """
    list_display = (
        'id', 'name', 'description', 'cover_image',
        'created_at', 'updated_at', 'rating_count', 'avg_rating'
    )
    search_fields = ('name', 'description')
    list_filter = ('created_at',)
    ordering = ('id',)
    readonly_fields = ('created_at', 'updated_at', 'rating_count', 'avg_rating')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'cover_image')
        }),
        ('Time Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Rating Statistics (Read-only)', {
            'fields': ('rating_count', 'avg_rating'),
            'classes': ('collapse',)
        }),
    )
    actions = [export_as_csv]  # Add CSV export action

    # Custom field: Count total ratings for the city
    def rating_count(self, obj):
        return CityRating.objects.filter(city=obj).count()
    rating_count.short_description = "Rating Count"

    # Custom field: Calculate average rating for the city
    def avg_rating(self, obj):
        ratings = CityRating.objects.filter(city=obj).values_list('rating', flat=True)
        if not ratings:
            return "No ratings"
        avg = sum(ratings) / len(ratings)
        return f"{avg:.1f} Stars"
    avg_rating.short_description = "Average Rating"

# 2. AttractionAdmin
@admin.register(Attraction)
class AttractionAdmin(admin.ModelAdmin):
    """
    Attraction model backend management configuration class
    Associate City model, support filtering/searching by city + bookmark statistics
    """
    list_display = (
        'id', 'name', 'city', 'description', 'official_url',
        'cover_image', 'bookmark_count'
    )
    search_fields = ('name', 'description', 'city__name')
    list_filter = ('city',)
    ordering = ('city__name', 'id')
    fieldsets = (
        ('Relevant City', {
            'fields': ('city',)
        }),
        ('Attraction Information', {
            'fields': ('name', 'description', 'official_url', 'cover_image')
        }),
    )
    fields = ('city', 'name', 'description', 'official_url', 'cover_image')  # Fast operation fields
    actions = [export_as_csv]  # Add CSV export action

    # Custom field: Count total bookmarks for the attraction
    def bookmark_count(self, obj):
        return Bookmark.objects.filter(attraction=obj).count()
    bookmark_count.short_description = "Bookmark Count"

# 3. CityRatingAdmin
@admin.register(CityRating)
class CityRatingAdmin(admin.ModelAdmin):
    """
    City rating model backend management configuration class
    Associate User/City models, display user ratings with star visualization
    """
    list_display = ('id', 'user', 'city', 'rating_star', 'created_at')
    search_fields = ('user__username', 'city__name')
    list_filter = ('rating', 'created_at', 'city')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    actions = [export_as_csv]  # Add CSV export action

    # Custom field: Visualize rating with stars
    def rating_star(self, obj):
        stars = "★" * obj.rating + "☆" * (5 - obj.rating)
        return format_html(f"<span style='color: #ffc107;'>{stars}</span>")
    rating_star.short_description = "Rating (Stars)"

    # Prohibit deletion of rating data
    def has_delete_permission(self, request, obj=None):
        return False

# 4. AttractionRatingAdmin
@admin.register(AttractionRating)
class AttractionRatingAdmin(admin.ModelAdmin):
    """
    Attraction rating model backend management configuration class
    Associate User/Attraction models, manage user ratings with star visualization
    """
    list_display = ('id', 'user', 'attraction', 'rating_star', 'created_at')
    search_fields = ('user__username', 'attraction__name')
    list_filter = ('rating', 'created_at', 'attraction__city')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    actions = [export_as_csv]  # Add CSV export action

    # Custom field: Visualize rating with stars
    def rating_star(self, obj):
        stars = "★" * obj.rating + "☆" * (5 - obj.rating)
        return format_html(f"<span style='color: #ffc107;'>{stars}</span>")
    rating_star.short_description = "Rating (Stars)"

    # Prohibit deletion of rating data
    def has_delete_permission(self, request, obj=None):
        return False

# 5. BookmarkAdmin
@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    """
    Bookmark model backend management configuration class
    Associate User/Attraction models, manage favorite data with permission control
    """
    list_display = ('id', 'user', 'attraction', 'attraction_city', 'created_at')
    search_fields = ('user__username', 'attraction__name', 'attraction__city__name')
    list_filter = ('created_at', 'attraction__city')
    readonly_fields = ('created_at', 'attraction_city')
    ordering = ('-created_at',)
    actions = [export_as_csv]  # Add CSV export action
    fields = ('user', 'attraction', 'created_at', 'attraction_city')

    # Custom field: Display attraction's city for easier filtering
    def attraction_city(self, obj):
        return obj.attraction.city.name
    attraction_city.short_description = "Attraction City"

    # Prohibit editing of bookmark data (display only)
    def has_change_permission(self, request, obj=None):
        return False

    # Allow deletion only for superusers
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser