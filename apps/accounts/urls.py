from django.urls import path, re_path
from .views import *

urlpatterns = [
    path('user_list/', user_list),
    path('user/<str:username>/', user_list),
    path('user_profile/', profile),
]
