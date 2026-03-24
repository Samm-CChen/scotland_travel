from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Avg, Count

from .models import City, Attraction, CityRating, Bookmark
from .serializers import CityRatingSerializer, BookmarkSerializer


class TravelViewsTestCase(TestCase):
    """Test cases for travel app views"""

    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )

        # Create test city
        self.city = City.objects.create(
            name='Edinburgh',
            description='Scottish capital',
            cover_image='https://example.com/edinburgh.jpg'
        )

        # Create test attraction
        self.attraction = Attraction.objects.create(
            city=self.city,
            name='Edinburgh Castle',
            description='Famous castle',
            official_url='https://edinburghcastle.scot',
            cover_image='https://example.com/castle.jpg'
        )

        # Initialize test client
        self.client = Client()

    def test_city_list_view(self):
        """Test city list view returns 200 OK and contains city data"""
        response = self.client.get(reverse('travel:cities'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edinburgh')
        self.assertTemplateUsed(response, 'travel/cities.html')

    def test_city_detail_view(self):
        """Test city detail view displays city and attraction data"""
        response = self.client.get(reverse('travel:city_detail', args=[self.city.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edinburgh Castle')
        self.assertTemplateUsed(response, 'travel/city_detail.html')

    def test_city_rating_submit_authenticated(self):
        """Test authenticated user can submit city rating"""
        # Login test user
        self.client.login(username='testuser', password='testpassword123')

        # Submit rating via AJAX
        response = self.client.post(
            reverse('travel:city_rating_submit'),
            {'city': self.city.id, 'rating': 5},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        self.assertEqual(response.json()['avg_rating'], 5.0)
        self.assertEqual(response.json()['rating_count'], 1)

        # Verify database update
        rating = CityRating.objects.get(user=self.user, city=self.city)
        self.assertEqual(rating.rating, 5)

    def test_city_rating_submit_unauthenticated(self):
        """Test unauthenticated user is redirected from rating submission"""
        response = self.client.post(
            reverse('travel:city_rating_submit'),
            {'city': self.city.id, 'rating': 5},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        # Should return 403 Forbidden (login required)
        self.assertEqual(response.status_code, 403)

    def test_bookmark_toggle(self):
        """Test bookmark toggle (add/remove) functionality"""
        self.client.login(username='testuser', password='testpassword123')

        # Add bookmark
        add_response = self.client.post(
            reverse('travel:bookmark_toggle'),
            {'attraction': self.attraction.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(add_response.json()['status'], 'bookmarked')
        self.assertTrue(Bookmark.objects.filter(user=self.user, attraction=self.attraction).exists())

        # Remove bookmark
        remove_response = self.client.post(
            reverse('travel:bookmark_toggle'),
            {'attraction': self.attraction.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(remove_response.json()['status'], 'unbookmarked')
        self.assertFalse(Bookmark.objects.filter(user=self.user, attraction=self.attraction).exists())

    def test_attraction_detail_view(self):
        """Test attraction detail view displays bookmark status"""
        self.client.login(username='testuser', password='testpassword123')

        # Add bookmark first
        Bookmark.objects.create(user=self.user, attraction=self.attraction)

        # Access detail view
        response = self.client.get(reverse('travel:attraction_detail', args=[self.attraction.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Added to bookmarks')  # Verify bookmark status display

class TravelSerializersTestCase(TestCase):
    """Test cases for travel app serializers"""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='test123')
        self.city = City.objects.create(name='Glasgow', description='Scottish city')

    def test_city_rating_serializer_validation(self):
        """Test city rating serializer validates 1-5 star range"""
        # Invalid rating (0 stars)
        invalid_data = {'city': self.city.id, 'rating': 0}
        serializer = CityRatingSerializer(data=invalid_data, context={'request': self.client.request()})
        self.assertFalse(serializer.is_valid())
        self.assertIn('rating', serializer.errors)

        # Valid rating (3 stars)
        valid_data = {'city': self.city.id, 'rating': 3}
        serializer = CityRatingSerializer(data=valid_data, context={'request': self.client.request()})
        self.assertTrue(serializer.is_valid())

    def test_bookmark_serializer_toggle(self):
        """Test bookmark serializer toggles bookmarks correctly"""
        attraction = Attraction.objects.create(city=self.city, name='Kelvingrove Art Gallery')

        # Add bookmark
        add_data = {'attraction': attraction.id}
        serializer = BookmarkSerializer(data=add_data, context={'request': self.client.request()})
        self.assertTrue(serializer.is_valid())
        result = serializer.save()
        self.assertEqual(result['status'], 'bookmarked')

        # Remove bookmark
        remove_data = {'attraction': attraction.id}
        serializer = BookmarkSerializer(data=remove_data, context={'request': self.client.request()})
        self.assertTrue(serializer.is_valid())
        result = serializer.save()
        self.assertEqual(result['status'], 'unbookmarked')