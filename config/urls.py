"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os
import json

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from main import views
from main.views.export_phrases_to_csv import export_phrases_to_csv_view
from django.conf.urls.i18n import i18n_patterns
from django.http import JsonResponse, HttpResponse
from django.http import FileResponse, Http404
from django.contrib.auth.decorators import login_required, user_passes_test
import base64
from django.contrib.auth import authenticate


def download_dbbackup_json(request):
    def extract_username_and_password(request):
        auth_header = request.META.get("HTTP_AUTHORIZATION")
        assert auth_header.startswith("Basic "), "Only basic authenticated is supported"
        encoded_credentials = auth_header.split(" ")[1]
        decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
        username, password = decoded_credentials.split(":", 1)
        return username, password

    username, password = extract_username_and_password(request)
    user = authenticate(request, username=username, password=password)
    assert user.is_superuser, "Only superusers can access this API"
    file_path = os.path.join(settings.BASE_DIR, "..", "dbbackup.json")

    # Check if the file exists
    if os.path.exists(file_path):
        # Use FileResponse to send the file for download
        response = FileResponse(open(file_path, "rb"))
        return response
    else:
        # Raise 404 if the file does not exist
        raise Http404("File does not exist")


urlpatterns = i18n_patterns(
    path(
        "download_dbbackup_json/", download_dbbackup_json, name="download_dbbackup_json"
    ),
    # 0
    path("admin/", admin.site.urls),  # this is like an add_one_phrase app
    # 1
    path(
        "<int:phrase_id>", views.practice_translation_view, name="practice_translation",
    ),
    path("", views.practice_translation_view, name="practice_translation"),
    # 2
    path(
        "export_phrases_to_csv/",
        export_phrases_to_csv_view,
        name="export_phrases_to_csv",
    ),
    # 3
    path(
        "import_from_readwise/",
        views.import_from_readwise_view,
        name="import_from_readwise",
    ),
    # 4
    path("assess_cefr_level/", views.assess_cefr_level_view, name="assess_cefr_level",),
    # 5
    path(
        "add_multiple_phrases/",
        views.add_multiple_phrases_view,
        name="add_multiple_phrases",
    ),
    # 6
    path(
        "create_study_materials/",
        views.create_study_materials_view,
        name="create_study_materials",
    ),
    # path(  # STOPPED USING THIS; TOO COMPLICATED TO MAINTAIN
    #     "collect_readwise_articles/",
    #     views.collect_readwise_articles_view,
    #     name="collect_readwise_articles",
    # ),
)

admin.site.site_header = "Fabulari"
admin.site.site_title = "Fabulari"
admin.site.index_title = "Tables"

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
