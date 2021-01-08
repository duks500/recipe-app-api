# allowes us to mock the database
# simulate the database is avialable
from unittest.mock import patch

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase


class CommandTests(TestCase):

    # Test what happend if we call the comand and
    # the database is already available
    def test_wait_for_db_ready(self):
        """Test waiting for db when db is available"""
        # Mock the behavior of the __getitem__ function
        # Just return true everytime it has been called
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.return_value = True
            # The name of the command that we have created
            call_command('wait_for_db')
            # Check that the __getitem__ is called one time
            self.assertEqual(gi.call_count, 1)

    # Mock the time.sleep, the same as with path... but return an argument
    @patch('time.sleep', return_value=True)
    # Check if the OperationalError raise an error, if yes:
    # wait 1 sec and try again
    def test_wait_for_db(self, ts):
        """Test waiting for db"""
        # Mock the behavior of the __getitem__ function
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            # side_effect will rasie an error 5 time and after will return true
            gi.side_effect = [OperationalError] * 5 + [True]
            # The name of the command that we have created
            call_command('wait_for_db')
            # Check that the __getitem__ is called 6 times
            self.assertEqual(gi.call_count, 6)
