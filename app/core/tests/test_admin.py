from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):

    # A setUp function is a function that runs before every other test function
    def setUp(self):
        # Set a client variable to self so we could use it again
        self.client = Client()
        # Create superuser
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@gmail.com',
            password='password123'
        )
        # Login the user (admin) using the Client helper function
        self.client.force_login(self.admin_user)
        # Create a regular user
        self.user = get_user_model().objects.create_user(
            email='test@gmail.com',
            password='password123',
            name='Test user full name'
        )

    def test_users_lister(self):
        """Test that users are listed on user page"""
        # Reverse is (APP:URL)
        # core_user_changelist is build into django
        url = reverse('admin:core_user_changelist')
        # will preforem an http get function to the url
        res = self.client.get(url)

        # Check that the responses contatin a certin item
        # Also look for HTTP200 response
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_user_change_page(self):
        """Test that user edit page works correctly"""
        # Url is going to be -> /admin/core/user/<id>
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        # Check if the response code is equal to HTTP-200(OK)
        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test that the create user page works correctly"""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        # Check if the response code is equal to HTTP-200(OK)
        self.assertEqual(res.status_code, 200)
