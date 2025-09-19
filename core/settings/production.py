from .base import *
import os

ROOT_URLCONF = 'core.urls'
# DATABASES = {"default": env.db("DATABASE_URL")}
"""DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'db.sqlite3',
        }
    }"""

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'postgres'),
        'USER': os.environ.get('POSTGRES_USER', 'unsql_admin'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD',"OZpb3Bf4zoTslo"),
        'HOST': os.environ.get('POSTGRES_HOST', 'unsql-postgres.postgres.database.azure.com'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432')
    }
}


GITHUB_ID = os.environ.get("GITHUB_ID",'')
GITHUB_SECRET = os.environ.get("GITHUB_SECRET",'')
GITHUB_AUTH = GITHUB_SECRET is not None and GITHUB_ID is not None

TWITTER_ID = os.getenv('TWITTER_ID', None)
TWITTER_SECRET = os.getenv('TWITTER_SECRET', None)
TWITTER_AUTH = TWITTER_SECRET is not None and TWITTER_ID is not None

SOCIALACCOUNT_PROVIDERS = {}
if GITHUB_AUTH:
    SOCIALACCOUNT_PROVIDERS['github'] = {
        'APP': {
            'client_id': GITHUB_ID,
            'secret': GITHUB_SECRET,
            'key': ''
        }
    }

if TWITTER_AUTH:
    SOCIALACCOUNT_PROVIDERS['twitter'] = {
        'APP': {
            'client_id': TWITTER_ID,
            'secret': TWITTER_SECRET,
            'key': ''
        }
    }

# AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN","dev-glybdgntuacarzbb.us.auth0.com")
# AUTH0_CLIENT_ID = os.environ.get("AUTH0_CLIENT_ID","nEYg15ldJKH3kPzf6n4uMxg5txakUl2D")
# AUTH0_CLIENT_SECRET = os.environ.get("AUTH0_CLIENT_SECRET","nvBqfST6psXX7W3PAFMwp-JN7ZHwgccUfcq_ryZTEFUeBv0WvSYDO-bPPIJeU-c4")
# AUTH0_MACHINE_DOMAIN = os.environ.get("AUTH0_MACHINE_DOMAIN","dev-glybdgntuacarzbb.us.auth0.com")
# AUTH0_MACHINE_ID = os.environ.get("AUTH0_MACHINE_ID","SIFZfaIUZMDHWYdFK8Vr6SaTrSdJCYKG")
# AUTH0_MACHINE_SECRET = os.environ.get("AUTH0_MACHINE_SECRET","NclqZmNBn-7qW7NtuhKEZEdyBvJqpxmSvLAgC16kuOM1n2AStUTYMJwPD7xKyjxz")
# AUDIENCE = os.environ.get('AUDIENCE','dev-glybdgntuacarzbb.us.auth0.com')

# STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY",'')
# STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY",'')
# STRIPE_ENDPOINT_SECRET=os.environ.get("STRIPE_ENDPOINT_SECRET","")

# STRIPE_PRODUCT_SOLO = os.environ.get("STRIPE_PRODUCT_SOLO")
# STRIPE_PRODUCT_TEAM_STARTER = os.environ.get("STRIPE_PRODUCT_TEAM_STARTER")
# STRIPE_PRICE_TEAM_STARTER = os.environ.get("STRIPE_PRICE_TEAM_STARTER")
# STRIPE_PRICE_SOLO = os.environ.get("STRIPE_PRICE_SOLO")

# STATIC_URL = '/static/'
# STATIC_ROOT = os.path.join(BASE_DIR, 'static')



from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

AUTH0_DOMAIN = os.environ["AUTH0_DOMAIN"]
AUTH0_CLIENT_ID = os.environ["AUTH0_CLIENT_ID"]
AUTH0_CLIENT_SECRET = os.environ["AUTH0_CLIENT_SECRET"]
AUTH0_MACHINE_DOMAIN = os.environ["AUTH0_MACHINE_DOMAIN"]
AUTH0_MACHINE_ID = os.environ["AUTH0_MACHINE_ID"]
AUTH0_MACHINE_SECRET = os.environ["AUTH0_MACHINE_SECRET"]
AUDIENCE = os.environ["AUDIENCE"]

STRIPE_PUBLISHABLE_KEY = os.environ["STRIPE_PUBLISHABLE_KEY"]
STRIPE_SECRET_KEY = os.environ["STRIPE_SECRET_KEY"]
STRIPE_ENDPOINT_SECRET = os.environ["STRIPE_ENDPOINT_SECRET"]

STRIPE_PRODUCT_SOLO = os.environ["STRIPE_PRODUCT_SOLO"]
STRIPE_PRODUCT_TEAM_STARTER = os.environ["STRIPE_PRODUCT_TEAM_STARTER"]
STRIPE_PRICE_TEAM_STARTER = os.environ["STRIPE_PRICE_TEAM_STARTER"]
STRIPE_PRICE_SOLO = os.environ["STRIPE_PRICE_SOLO"]

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')