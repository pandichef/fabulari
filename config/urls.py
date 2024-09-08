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
from django.contrib import admin
from django.urls import path
from main import views
from main.export_phrase_list import export_csv

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.prompt_view, name="prompt_view"),
    # path("download_csv/<int:pk>/", export_csv, name="download_csv"),
    path("export_csv/", export_csv, name="export_csv"),
    path("update_readwise/", views.update_readwise, name="update_readwise"),
    path("get_my_level/", views.get_my_level_view, name="get_my_level"),
    path(
        "add_multiple_phrases/", views.add_multiple_phrases, name="add_multiple_phrases"
    ),
    path(  # STOPPED USING THIS; TOO COMPLICATED TO MAINTAIN
        "collect_readwise_articles/",
        views.collect_readwise_articles_view,
        name="collect_readwise_articles",
    ),
    path("create_article/", views.create_article_view, name="create_article",),
]

admin.site.site_header = "Fabulari"
admin.site.site_title = "Fabulari"
admin.site.index_title = "Tables"
