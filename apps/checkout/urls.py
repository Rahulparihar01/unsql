from django.urls import path
from .views import *

urlpatterns = [
    path('success', PaymentSuccessView.as_view(), name='success'),
    path('failed/', PaymentFailedView.as_view(), name='failed'),
    path('subscription/',subscription_plane,name="subscription"),
    path("checkout/<id>/",subscription_checkout,name="checkout"),
    path("webhook/",stripe_webhook, name="webhook"),
    path("cancel/", cancel_checkout, name="cancel_checkout"),
]   