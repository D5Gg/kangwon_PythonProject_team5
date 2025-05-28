

from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("", views.mainPage),
    path("admin/", admin.site.urls),
    path("index/", views.index)
]
