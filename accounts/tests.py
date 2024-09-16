from django.test import TestCase

# Create your tests here.
import pytest
from django.contrib.auth.models import User


from django.contrib.auth import get_user_model


@pytest.mark.django_db
def test_create_user():
    # Get the custom or default User model
    User = get_user_model()

    # Create a user instance
    user = User(username="testuser", password="mypassword123")
    user.save()

    # Test the user's username
    assert user.username == "testuser"
    assert User.objects.count() == 1
