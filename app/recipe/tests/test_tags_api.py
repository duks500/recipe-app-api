from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer


TAG_URL = reverse('recipe:tag-list')


class PublicTagsApiTests(TestCase):
    """Test the publiclt avialable tags API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving tags"""
        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test the authorized user tags API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@rainwalk.io',
            'password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieveing tags"""
        # Create two tags
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAG_URL)

        # Order the list by name
        tags = Tag.objects.all().order_by('-name')
        # Send the list to the serializer
        serializer = TagSerializer(tags, many=True)
        # Check if the tags has been created
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Check if the res.data and the serializer.data are equal
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that tags returned are for the authenticated user"""
        # Create another user
        user2 = get_user_model().objects.create_user(
            'other@rainwalk.io',
            'testpass'
        )
        # Create new tags
        Tag.objects.create(user=user2, name='Fruity')
        tag = Tag.objects.create(user=self.user, name='Comfort Food')

        res = self.client.get(TAG_URL)

        # Check if the tags has been created
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Check if the leng of the data is 1 (=2)
        self.assertEqual(len(res.data), 1)
        # Check if the name of the tag in the res response is the user tag
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """Test creating a new tag"""
        payload = {
            'name': 'Test tag'
        }
        self.client.post(TAG_URL, payload)

        # Verify that thetag exists, if yes->dave it to exists
        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        # Return a true if the tag exists
        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """Test creating a new tag with invalid payload"""
        payload = {
            'name': ''
        }
        res = self.client.post(TAG_URL, payload)

        # Check if the response is 400
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
