# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, include
from . import views
from django.contrib.auth.views import LogoutView
from django.http import HttpResponse

urlpatterns = [
    path('register/', views.register_user, name="register"),
    path("home/", views.index, name="index"),
    path("login/", views.auth0login, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("callback/", views.callback, name="callback"),
    path("test/", views.test_data, name="test_data")
]
