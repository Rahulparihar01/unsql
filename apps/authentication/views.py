# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
#
# Create your views here.
import http.client

from django.contrib.auth import logout
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import CustomUser
from ..home.models import Connection
from ..home.forms import ConnectionForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm, SignUpForm
from apps.helpers import *
from apps import COMMON, helpers
# from django.settings import GITHUB_AUTH, TWITTER_AUTH

import json
from authlib.integrations.django_client import OAuth
from django.urls import reverse
from urllib.parse import quote_plus, urlencode
from stripe.error import SignatureVerificationError
import stripe
import requests
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from ..checkout.models import Product
from apps.auth_decorator import auth_decorator_func
from apps.auth import get_access_token,get_user_stripe_id_auth0,update_user_metadata

from datetime import datetime

oauth = OAuth()

oauth.register(
    "auth0",
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{settings.AUTH0_DOMAIN}/.well-known/openid-configuration",
)

# def auth0login(request):
#     return oauth.auth0.authorize_redirect(
#         request, request.build_absolute_uri(reverse("callback"))
#     )


import uuid
from django.core.cache import cache
from django.urls import reverse
from django.shortcuts import redirect

def auth0login(request):
    # Generate a unique state
    state = str(uuid.uuid4())
    request.session['oauth_state'] = state
    request.session.modified = True
    cache.set(f"oauth_state_{request.session.session_key}_{state}", state, timeout=300)  # 5 minutes
    print(f"DEBUG: Generated state: {state}, Session ID: {request.session.session_key}")
    
    return oauth.auth0.authorize_redirect(
        request,
        request.build_absolute_uri(reverse("callback")),
        state=state
    )

# def callback(request):
#     try:
#         # Get user info from session
#         auth0_id = request.session['auth0']['userinfo']['sub'].replace('auth0|', '')
#         email = request.session['auth0']['userinfo']['email']
        
#         # Get or create CustomUser
#         user = CustomUser.objects.filter(username=auth0_id).first()
#         if not user:
#             user = CustomUser.objects.create(
#                 username=auth0_id,
#                 email=email,
#                 is_active=True
#             )
            
#         # Redirect to the next URL if provided
#         next_url = request.GET.get('next', '/chat')
#         return redirect(next_url)
        
#     except Exception as e:
#         print(f"Error in callback: {str(e)}")
#         return redirect('login')




def callback(request):
    try:

        
        print("DEBUG: Exchanging code for token")
        print("DEBUG: Domain:", settings.AUTH0_DOMAIN)
        print("DEBUG: Client ID:", settings.AUTH0_CLIENT_ID)
        # Don't print secret in logs for safety
        print("DEBUG: Redirect URI:", request.build_absolute_uri(reverse("callback")))

        # Exchange code for token
        token = oauth.auth0.authorize_access_token(request)
        request.session["auth0"] = token
        userinfo = token.get("userinfo")

        if not userinfo:
            raise Exception("No userinfo returned from Auth0")

        auth0_id = userinfo["sub"].replace("auth0|", "")
        email = userinfo["email"]

        user = CustomUser.objects.filter(username=auth0_id).first()
        if not user:
            user = CustomUser.objects.create(
                username=auth0_id,
                email=email,
                is_active=True
            )

        # Handle Stripe cancellation case
        referer = request.META.get("HTTP_REFERER", "")
        if "stripe.com" in referer and "next" in request.session:
            del request.session["next"]
            return redirect("login")

        next_url = request.GET.get("next", "/chat")
        return redirect(next_url)

    except Exception as e:
        print(f"Error in callback: {str(e)}")
        return redirect("login")

# def callback(request):
#     try:
#         auth0_id = request.session['auth0']['userinfo']['sub'].replace('auth0|', '')
#         email = request.session['auth0']['userinfo']['email']
        
#         user = CustomUser.objects.filter(username=auth0_id).first()
#         if not user:
#             user = CustomUser.objects.create(
#                 username=auth0_id,
#                 email=email,
#                 is_active=True
#             )
            
#         # Check if coming from Stripe cancellation
#         referer = request.META.get('HTTP_REFERER', '')
#         if 'stripe.com' in referer and 'next' in request.session:
#             del request.session['next']
#             return redirect('login')
            
#         next_url = request.GET.get('next', '/chat')
#         return redirect(next_url)
        
#     except Exception as e:
#         print(f"Error in callback: {str(e)}")
#         return redirect('login')


@login_required
def logout_view(request):
    logout(request)
    return redirect('/')

def login_view(request):
    if "auth0" in request.session:
        return redirect("home/")
    form = LoginForm(request.POST or None)
    msg = None

    if request.method == "POST":

        if form.is_valid():

            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            user = authenticate(username=username, password=password)

            # Credentials ok
            is_suspended = False
            if user:
                # Check Suspension state
                if user.status == COMMON.USER_SUSPENDED:
                    is_suspended = True
                    msg = 'Suspended account. Please contact support.'
                # All good
                else:

                    user.failed_logins = 0
                    user.save()
                    login(request, user)
                    return redirect("/")

            # Check user is registered
            user = username_exists(username)
            if not user:
                user = email_exists(username)
            # If user is suspended, don't check this case
            if not is_suspended:
                if user:

                    msg = 'Wrong password.'

                    # Update the fraud counter
                    user.failed_logins += 1

                    # Suspend the user (if needed)
                    if user.failed_logins > 4: #cfg_LOGIN_ATTEMPTS():
                       user.status = COMMON.USER_SUSPENDED
                       msg = 'Suspended account. Please contact support.'



                    # Update user
                    user.save()

                else:

                    msg = 'Username not registered.'

        else:
            msg = 'Error validating the form'
    else:
        msg = request.GET.get('message', None)

    return render(request, "accounts/login.html", {"form": form, "msg": msg,
                                                   # "github_login": GITHUB_AUTH,
                                                   "github_login":False,
                                                   "twitter_login": settings.TWITTER_AUTH,"auth0_login":True})

def register_user(request):
    msg = None
    success = False

    # new Registration
    if request.method == "POST":
        form = SignUpForm(request.POST)

        if form.is_valid():

            form.save()

            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")

            user = authenticate(username=username, password=raw_password)

            msg = 'User created successfully.'
            success = True

            # return redirect("/login/")

        else:
            msg = 'Form is not valid'
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})

#
# def change_password(request, **kwargs):
#
#     form = SetPasswordForm(user=request.user, data=request.POST)
#     if form.is_valid():
#         user = form.save()
#         update_session_auth_hash(request, user)
#         message = 'Password successfully changed.'
#         status = 200
#     else:
#         message = form.errors
#         status = 400
#     return JsonResponse({
#         'message': message
#     }, status=status)
#
#
# def delete_account(request, **kwargs):
#     result, message = helpers.delete_user(request.user.username)
#     if not result:
#         return JsonResponse({
#             'errors': message
#         }, status=400)
#     logout(request)
#     return HttpResponseRedirect('home')
#
# def test(request):
#     return HttpResponse("jdjdj")

@auth_decorator_func
def index(request):
    return render(
        request,
        "index.html",
        context={
            "session": request.session.get("auth0"),
            "pretty": json.dumps(request.session.get("auth0"), indent=4),
        },
    )

def home(request):
    return HttpResponse("htttp tesponse")


@csrf_exempt
def stripe_webhook(request):
    if request.method=='POST':
        stripe.api_key = settings.STRIPE_SECRET_KEY
        endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        try:
            event = json.loads(payload)
        except:
            print('⚠️  Webhook error while parsing basic request.')
            return HttpResponse(status=404)
        if endpoint_secret:
            # Only verify the event if there is an endpoint secret defined
            # Otherwise use the basic event deserialized with json
            sig_header = request.headers.get('stripe-signature')
            try:
                event = stripe.Webhook.construct_event(
                    payload, sig_header, endpoint_secret
                )
            except stripe.error.SignatureVerificationError as e:
                print('⚠️  Webhook signature verification failed.' + str(e))
                return HttpResponse(status=404)
        if event and event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            user_id = session['metadata']['user_id']
            stripe_customer_id = session['customer']
            update_user_metadata(user_id,stripe_customer_id)
            """x = send_mail(
                subject="Here is your product",
                message=f"Thanks for your purchase. The URL is: http//:localhost",
                recipient_list=["karkipramish18@gmail.com"],
                from_email="tutee.line@gmail.com",
                fail_silently=False,
            )
            print(x)"""
        return HttpResponse(status=200)

def test_data(request):
    return render(request,"checkouts/subscription.html")