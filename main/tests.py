from django.test import TestCase

# Create your tests here.
import pytest
from django.contrib.auth.models import User
from main.models import Phrase

from django.contrib.auth import get_user_model


@pytest.mark.django_db
def test_create_phrase():
    User = get_user_model()
    user = User()
    user.save()
    phrase = Phrase(user=user, raw_text="como estas")
    phrase.save()
    assert Phrase.objects.count() == 1
    assert Phrase.objects.first().raw_text == "como estas"
    assert Phrase.objects.first().cleaned_text == ""
    assert Phrase.objects.first().user == user
