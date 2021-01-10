from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


# URL constant
CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


# Create user helper function
# **params mean that we can add more variables later on
def create_user(**params):
    return get_user_model().objects.create_user(**params)


# Public=Unautenticate and Priavey=Authanticate
class PublicUserApiTests(TestCase):
    """Test the user API (public)"""

    # Setup function to call the client api
    def setUp(self):
        self.client = APIClient()

    # Check if the user created successfuly
    def test_create_vaild_user_success(self):
        """Test creating user with valid payload is successful"""
        payload = {
            'email': 'test@rainwalk.io',
            'password': 'testpass',
            'name': 'Test name'
        }
        # A request
        res = self.client.post(CREATE_USER_URL, payload)

        # Check if the outcome is created(201)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # Take the paylod, create a user and check if the user is created
        user = get_user_model().objects.get(**res.data)
        # Check if the password is correct
        self.assertTrue(user.check_password(payload['password']))
        # Check that the password is not return (safety check)
        self.assertNotIn('password', res.data)

    # Check if user already exists
    def test_user_exists(self):
        """Test creating user that already exists fails"""
        payload = {
            'email': 'test@rainwalk.io',
            'password': 'testpass',
            'name': 'Test'
        }
        # Creat a new user
        create_user(**payload)

        # Post request
        res = self.client.post(CREATE_USER_URL, payload)

        # Looking for 400 becasue the user already exists
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # Check if password is shorter than 5 char
    def test_password_too_short(self):
        """Test that password must be more than 5 characters"""
        payload = {
            'email': 'test@rainwalk.io',
            'password': 'pw',
            'name': 'Test'
        }
        # Post request
        res = self.client.post(CREATE_USER_URL, payload)

        # Looking for 400 becasue the password is too short
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # Check if the user was ever existsted (return false if no user)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        )
        self.assertFalse(user_exists)

    # Check for creating a new token
    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        payload = {
            'email': 'test@rainwalk.io',
            'password': 'testpass',
            'name': 'Test'
        }
        # Creat a new user
        create_user(**payload)
        # Post request
        res = self.client.post(TOKEN_URL, payload)

        # Check if there is a key name 'token' in the response data
        self.assertIn('token', res.data)
        # Check if the outcome is created(201)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given"""
        # Creat a new user
        create_user(email='test@rainwalk.io', password='testpass')
        payload = {
            'email': 'test@rainwalk.io',
            'password': 'wrong',
            'name': 'Test'
        }
        # Post request
        res = self.client.post(TOKEN_URL, payload)

        # Check if the 'token' is not in the response data
        self.assertNotIn('token', res.data)
        # Looking for 400 becasue the token is not existed
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token is not created if user doesn't exist"""
        payload = {
            'email': 'test@rainwalk.io',
            'password': 'testpass',
            'name': 'Test'
        }
        # Post request
        res = self.client.post(TOKEN_URL, payload)

        # Check if the 'token' is not in the response data
        self.assertNotIn('token', res.data)
        # Looking for 400 becasue the user is not existed
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that email and password are required"""
        payload = {
            'email': 'one',
            'password': '',
            'name': 'Test'
        }
        # Post request
        res = self.client.post(TOKEN_URL, payload)

        # Check if the 'token' is not in the response data
        self.assertNotIn('token', res.data)
        # Looking for 400 becasue the user is not existed (bad email and pasw)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test that authentication is required for users"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API requests that reuire authentication"""

    def setUp(self):
        self.user = create_user(
            email='test@rainwalk.io',
            password='testpass',
            name='name'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retriveing profile for logged in used"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_me_not_allowed(self):
        """Test that POST is not allowed on the url"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_progile(self):
        """Test updating the user profile for authentivated user"""
        payload = {
            'name': 'new name',
            'password': 'newpassword123'
        }
        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
