from django.http.response import HttpResponseNotFound, JsonResponse,HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.urls import reverse, reverse_lazy
from .models import *
from django.views.generic import ListView, CreateView, DetailView, TemplateView
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json
from apps.auth import update_user_metadata
from django.core.mail import send_mail
# Create your views here.
from ..home.models import Auth0User
from apps.authentication.models import CustomUser

stripe.api_key = settings.STRIPE_SECRET_KEY

def subscription_plane(request):
    #"{% url 'checkout'  id=1%}"
    return redirect(reverse_lazy('checkout', kwargs={'id': 1}))
    #return render(request, "checkouts/subscription.html")

# @csrf_exempt
# def subscription_checkout(request,id):
#     price,product = subscription_price(id)
#     #print(settings.STRIPE_SECRET_KEY)

#     try:
#         # Get user from session
#         auth0_id = request.session['auth0']['userinfo']['sub'].replace('auth0|', '')
#         email = request.session['auth0']['userinfo']['email']
        
#         # Get or create user
#         user = CustomUser.objects.get_or_create(
#             username=auth0_id,
#             defaults={'email': email, 'is_active': True}
#         )[0]
        
#         # Create Stripe customer if needed
#         if not hasattr(user, 'stripe_customer_id') or not user.stripe_customer_id:
#             customer = stripe.Customer.create(
#                 email=email,
#                 metadata={'auth0_id': auth0_id}
#             )
#             user.stripe_customer_id = customer.id
#             user.save()
        
#         # Create Stripe checkout session
#         session = stripe.checkout.Session.create(
#             customer=user.stripe_customer_id,
#             payment_method_types=['card'],
#             line_items=[{
#                 'price': price,
#                 # For metered billing, do not pass quantity
#                 'quantity': 1
#             }],
#             metadata={
#                 'user_id': auth0_id
#             },
#             mode='subscription',
#             success_url=request.build_absolute_uri(
#                 reverse('success')
#             ) + "?session_id={CHECKOUT_SESSION_ID}",
#             cancel_url=request.build_absolute_uri(reverse('failed')),
#             #cancel_url=request.build_absolute_uri(reverse('/'))
#         )
        
#         return redirect(session.url, code=303)
        
#     except Exception as e:
#         print(e)
#         return HttpResponse("failed")
def cancel_checkout(request):
    if 'next' in request.session:
        del request.session['next']
    return redirect('login')

@csrf_exempt
def subscription_checkout(request, id):
    price, product = subscription_price(id)

    try:
        auth0_id = request.session['auth0']['userinfo']['sub'].replace('auth0|', '')
        email = request.session['auth0']['userinfo']['email']
        
        user = CustomUser.objects.get_or_create(
            username=auth0_id,
            defaults={'email': email, 'is_active': True}
        )[0]
        
        if not hasattr(user, 'stripe_customer_id') or not user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=email,
                metadata={'auth0_id': auth0_id}
            )
            user.stripe_customer_id = customer.id
            user.save()
        
        session = stripe.checkout.Session.create(
            customer=user.stripe_customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price': price,
                'quantity': 1
            }],
            metadata={'user_id': auth0_id},
            mode='subscription',
            success_url=request.build_absolute_uri(reverse('success')) + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.build_absolute_uri(reverse('cancel_checkout')),  # Custom cancel view
        )
        
        return redirect(session.url, code=303)
        
    except Exception as e:
        print(e)
        return HttpResponse("failed")


def subscription_price(id):
    if id=="1":
        return settings.STRIPE_PRICE_SOLO, settings.STRIPE_PRODUCT_SOLO #"prod_O0lQ7aZ79JXpsf"
    elif id=="2":
        return settings.STRIPE_PRICE_TEAM_STARTER, settings.STRIPE_PRODUCT_TEAM_STARTER #"prod_O0lQ8YOUjddsKU"


@csrf_exempt
def stripe_webhook(request):
    if request.method=='POST':
        print("DEBUG: Webhook recieved.")
        stripe.api_key = settings.STRIPE_SECRET_KEY
        endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
        #print(stripe.api_key)
        #print(endpoint_secret)
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
            updated_auth=update_user_metadata(user_id,stripe_customer_id)

            try:
                subscription = stripe.Subscription.retrieve(session.subscription)
                customer = stripe.Customer.retrieve(stripe_customer_id)
                auth0_id = customer.metadata.get('auth0_id')
                
                if auth0_id:
                    user = CustomUser.objects.filter(username=auth0_id).first()
                    if user:
                        user.stripe_customer_id = stripe_customer_id
                        user.save()
                        
                    update_user_metadata(auth0_id, stripe_customer_id)
                    
            except Exception as e:
                print(f"Error processing webhook: {str(e)}")
                return HttpResponse(status=500)

        return HttpResponse(status=200)


class PaymentSuccessView(TemplateView):
    template_name = "checkouts/payment_success.html"
    #template_name = "home/index.html"

    def get(self, request, *args, **kwargs):
        session_id = request.GET.get('session_id')
        if session_id is None:
            return HttpResponseNotFound()

        stripe.api_key = settings.STRIPE_SECRET_KEY
        session = stripe.checkout.Session.retrieve(session_id)

        # order = get_object_or_404(OrderDetail, stripe_payment_intent=session.payment_intent)
        # order.has_paid = True
        # order.save()
        #return render(request, self.template_name)
        # return the template with value "user_id" as the context
        print("about to return...")
        return render(request, self.template_name, {'user_id': request.session['auth0']['userinfo']['sub'].replace('auth0|', '')})

class PaymentFailedView(TemplateView):
    #template_name = "home/index.html"
    def get(self, request, *args, **kwargs):
        return redirect("https://app.unsql.ai")
    #template_name = "checkouts/payment_failed.html"

from django.shortcuts import render

def payment_portal(request):
    return render(request, "checkouts/payment_portal.html")
