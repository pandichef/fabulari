from django.test import TestCase

# Create your tests here.
import pytest

# from django.contrib.auth.models import User
from accounts.admin import CustomUserAdmin
from django.test import RequestFactory
from django.contrib.auth import get_user_model


@pytest.mark.django_db
def test_create_user():
    User = get_user_model()
    user = User(username="testuser")
    user.save()
    # assert user.username == ""
    assert User.objects.count() == 1
    assert User.objects.first().username == "testuser"


# @pytest.mark.django_db
# def test_create_user_via_admin():
#     request = RequestFactory().get("")
#     cua = CustomUserAdmin()
#     # CustomUserAdmin.save_model
#     # def save_model(self, request, obj, form, change)

#     # User = get_user_model()
#     # user = User(username="testuser")
#     # user.save()
#     # # assert user.username == ""
#     # assert User.objects.count() == 1
#     # assert User.objects.first().username == "testuser"

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client


@pytest.fixture
def admin_user(db):
    """Create a superuser for testing purposes."""
    User = get_user_model()
    return User.objects.create_superuser(
        username="admin", email="admin@example.com", password="password123"
    )


@pytest.fixture
def client_admin_logged_in(admin_user):
    """Log in the admin user to the Django admin site."""
    client = Client()
    client.login(username=admin_user.username, password="password123")
    return client


@pytest.mark.django_db
def test_create_user_in_admin(client_admin_logged_in):
    """Test creating a user through the Django admin site."""
    # Prepare the data for the new user
    user_data = {
        "username": "testuser",
        "password1": "something_very_secretive123$%^",  # Use the correct field names
        "password2": "something_very_secretive123$%^",  # Use the correct field names
        "email": "testuser@example.com",
        "is_staff": "1",  # Use '1' or 'on' for checkbox fields
        "is_active": "1",
        "_save": "Save",  # Include the submit button name
    }

    # Use the client to access the admin user creation page
    url = reverse("admin:accounts_customuser_add")
    response = client_admin_logged_in.post(url, user_data)

    # Check if the form submission was successful (302 means redirection after success)
    assert (
        response.status_code == 302
    ), f"Form errors: {response.context['adminform'].form.errors}"

    # Verify that the user was created
    User = get_user_model()
    assert User.objects.filter(username="testuser").exists()
