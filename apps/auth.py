from django.conf import settings
import requests
from apps.authentication.models import CustomUser
import urllib

def get_access_token():
    try:
        payload = {
            'client_id': settings.AUTH0_MACHINE_ID,  # Use machine-to-machine credentials
            'client_secret': settings.AUTH0_MACHINE_SECRET,
            'audience': 'https://dev-3os1nnxqyzdrygtf.us.auth0.com/api/v2/',
            'grant_type': 'client_credentials',
        }
        
        response = requests.post(
            f'https://{settings.AUTH0_DOMAIN}/oauth/token',
            json=payload
        )
        response.raise_for_status()
        print("DEBUG: Token response:", response.json())
        return response.json()['access_token']
    except Exception as e:
        print("DEBUG: Token error:", str(e))
        return None

def get_user_stripe_id_auth0(user_id):
    try:
        # Try database first
        user = CustomUser.objects.filter(username=user_id.replace('auth0|', '')).first()
        if user and hasattr(user, 'stripe_customer_id') and user.stripe_customer_id:
            print("DEBUG: Found stripe ID in database:", user.stripe_customer_id)
            return user.stripe_customer_id
            
        # Try Auth0
        access_token = get_access_token()
        if not access_token:
            print("DEBUG: No access token obtained")
            return {'status': 'failed', 'error': 'No access token'}
            
        encoded_user_id = urllib.parse.quote(user_id)
        url = f'https://{settings.AUTH0_DOMAIN}/api/v2/users/{encoded_user_id}'
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        print("DEBUG: Making API request to:", url)
        response = requests.get(url, headers=headers)
        print("DEBUG: Response status:", response.status_code)
        print("DEBUG: Response body:", response.text)

        response.raise_for_status()
        
        user_data = response.json()

        print("DEBUG: User data keys:", user_data.keys())
        if 'user_metadata' in user_data and 'stripe_customer_id' in user_data['user_metadata']:
            stripe_id = user_data['user_metadata']['stripe_customer_id']
            # Save to database
            if user:
                user.stripe_customer_id = stripe_id
                user.save()
            return stripe_id
            
        return {'status': 'failed', 'error': 'No stripe ID found'}
    except Exception as e:
        print("DEBUG: Error getting stripe ID:", str(e))
        return {'status': 'failed', 'error': str(e)}

def update_user_metadata(user_id, stripe_customer_id):
    try:
        # Update local user
        user = CustomUser.objects.filter(username=user_id.replace('auth0|', '')).first()
        if user:
            user.stripe_customer_id = stripe_customer_id
            user.save()
            
        # Update Auth0 user
        access_token = get_access_token()
        if not access_token:
            return {'status': 'failed', 'error': 'No access token'}
            
        encoded_user_id = urllib.parse.quote("auth0|" + str(user_id))
        url = f'https://{settings.AUTH0_DOMAIN}/api/v2/users/{encoded_user_id}'
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'user_metadata': {
                'stripe_customer_id': stripe_customer_id
            }
        }
        
        response = requests.patch(url, headers=headers, json=data)
        response.raise_for_status()
        
        return {'status': 'success'}
    except Exception as e:
        print("DEBUG: Error updating metadata:", str(e))
        return {'status': 'failed', 'error': str(e)}