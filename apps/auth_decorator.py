from functools import wraps
from django.shortcuts import redirect
import json
import stripe
from .auth import get_user_stripe_id_auth0
from apps.authentication.models import CustomUser
from django.conf import settings
from django.urls import reverse, reverse_lazy
from django.http import JsonResponse

# def auth_decorator_func(view_func):
#     @wraps(view_func)
#     def wrapper(request, *args, **kwargs):
#         print("DEBUG: Entering auth decorator")
#         print("DEBUG: Request headers:", dict(request.headers))
        
#         # Check if this is an AJAX request
#         is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
#         print("DEBUG: Is AJAX request:", is_ajax)
        
#         # Get the login URL
#         login_url = reverse('login')
        
#         # Special handling for /chat/login path
#         if request.path.startswith('/chat/login'):
#             return redirect(login_url)
        
#         # Check if we're already on a login-related path
#         if request.path.startswith(login_url) or '/login' in request.path:
#             # If we're already on a login page, don't redirect
#             return view_func(request, *args, **kwargs)
            
#         # Check if user is authenticated via Auth0
#         if 'auth0' not in request.session:
#             print("DEBUG: No auth0 session found")
#             if is_ajax:
#                 return JsonResponse({"error": "Not authenticated"}, status=401)
            
#             # Store the original URL to redirect back after login
#             request.session['next'] = request.path
#             return redirect(login_url)
            
#         try:
#             # Get or create CustomUser
#             auth0_id = request.session['auth0']['userinfo']['sub'].replace('auth0|', '')
#             email = request.session['auth0']['userinfo']['email']
            
#             try:
#                 user = CustomUser.objects.get(
#                     username=auth0_id,
#                     email=email
#                 )
#             except CustomUser.DoesNotExist:
#                 user = CustomUser.objects.create(
#                     username=auth0_id,
#                     email=email,
#                     is_active=True
#                 )
            
#             # Check if we're coming from Stripe checkout (check referer)
#             referer = request.META.get('HTTP_REFERER', '')
#             if 'stripe.com' in referer:
#                 # If coming from Stripe, clear any stored next URL and redirect to login
#                 if 'next' in request.session:
#                     del request.session['next']
#                 return redirect(login_url)
            
#             # Check Stripe subscription
#             stripe_id = get_user_stripe_id_auth0(request.session['auth0']['userinfo']['sub'])
#             print("DEBUG: Found stripe ID in database:", stripe_id)
#             print("DEBUG: Stripe ID response:", stripe_id)
            
#             # Handle the metadata error case
#             if isinstance(stripe_id, dict) and stripe_id.get('status') == 'failed':
#                 # If we have a stripe ID in our DB, use that
#                 if user.stripe_customer_id:
#                     stripe_id = user.stripe_customer_id
#                 else:
#                     print("DEBUG: No stripe customer ID found")
#                     if is_ajax:
#                         return JsonResponse({"error": "Subscription required"}, status=402)
#                     return redirect(reverse_lazy('checkout', kwargs={'id': 1}))
            
#             if not stripe_id or isinstance(stripe_id, dict):
#                 if is_ajax:
#                     return JsonResponse({"error": "Subscription required"}, status=402)
#                 return redirect(reverse('payment_portal'))
                
#             # Check if subscription is active
#             stripe.api_key = settings.STRIPE_SECRET_KEY
#             subscriptions = stripe.Subscription.list(
#                 customer=stripe_id,
#                 status='active',
#                 limit=1
#             )
            
#             if not subscriptions.data:
#                 if is_ajax:
#                     return JsonResponse({"error": "Subscription required"}, status=402)
#                 return redirect(reverse('payment_portal'))
                
#             return view_func(request, *args, **kwargs)
            
#         except Exception as e:
#             print(f"Error in auth decorator: {str(e)}")
#             if is_ajax:
#                 return JsonResponse({"error": "Internal Server Error"}, status=500)
#             return redirect(reverse('login'))
            
#     return wrapper
import logging
logger = logging.getLogger('apps.authentication')
def auth_decorator_func(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        print("DEBUG: Entering auth decorator")
        # print("DEBUG: Request headers:", dict(request.headers))
        
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        login_url = reverse('login')
        if request.path == '/':
            logger.debug("Skipping auth check for homepage")
            return view_func(request, *args, **kwargs)
        
        if request.path.startswith('/chat/login'):
            return redirect(login_url)
        
        if request.path.startswith(login_url) or '/login' in request.path:
            return view_func(request, *args, **kwargs)
            
        if 'auth0' not in request.session:
            print("DEBUG: No auth0 session found")
            if is_ajax:
                return JsonResponse({"error": "Not authenticated"}, status=401)
            
            referer = request.META.get('HTTP_REFERER', '')
            if 'stripe.com' in referer and 'next' in request.session:
                del request.session['next']  # Clear next URL on Stripe back
            request.session['next'] = request.path
            return redirect(login_url)
            
        try:
            auth0_id = request.session['auth0']['userinfo']['sub'].replace('auth0|', '')
            email = request.session['auth0']['userinfo']['email']
            
            user = CustomUser.objects.get(username=auth0_id, email=email)
            
            referer = request.META.get('HTTP_REFERER', '')
            if 'stripe.com' in referer:
                if 'next' in request.session:
                    del request.session['next']
                return redirect(login_url)  # Force redirect to login on Stripe back
            
            stripe_id = get_user_stripe_id_auth0(request.session['auth0']['userinfo']['sub'])
            if isinstance(stripe_id, dict) and stripe_id.get('status') == 'failed':
                if user.stripe_customer_id:
                    stripe_id = user.stripe_customer_id
                else:
                    if is_ajax:
                        return JsonResponse({"error": "Subscription required"}, status=402)
                    return redirect(reverse_lazy('checkout', kwargs={'id': 1}))
            
            if not stripe_id or isinstance(stripe_id, dict):
                if is_ajax:
                    return JsonResponse({"error": "Subscription required"}, status=402)
                # return redirect(reverse('payment_portal'))
                return redirect(reverse_lazy('checkout', kwargs={'id': 1}))

                
            stripe.api_key = settings.STRIPE_SECRET_KEY
            subscriptions = stripe.Subscription.list(customer=stripe_id, status='active', limit=1)
            if not subscriptions.data:
                if is_ajax:
                    return JsonResponse({"error": "Subscription required"}, status=402)
                # return redirect(reverse('payment_portal'))  
                return redirect(reverse_lazy('checkout', kwargs={'id': 1}))

                
            return view_func(request, *args, **kwargs)
            
        except Exception as e:
            print(f"Error in auth decorator: {str(e)}")
            if is_ajax:
                return JsonResponse({"error": "Internal Server Error"}, status=500)
            return redirect(reverse('login'))
            
    return wrapper