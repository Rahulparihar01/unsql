# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views
from apps.home import retell_api
from apps.checkout import views as checkout_views

# from apps.home import whatsapp_api

urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('create-postgres-connection.html', views.create_postgres_connection, name='create-postgres-connection'),
    path('connections.html', views.connections, name='connections'),
    path('chat', views.chat, name='chat'),  
    path('new_chat', views.new_chat, name='new_chat'),
    path('chat/<int:connection_id>/', views.chat, name='chat_with_connection'),
    path('new-message/', views.new_message, name='new_message'),
    path('execute-sql/', views.execute_sql, name='execute_sql'),
    path('get_chat_messages', views.get_chat_messages, name='get_chat_messages'),
    path('generate_sample_data', views.generate_sample_data, name='generate_sample_data'),
    path('visualization', views.visualize, name='visualization'),  # Remove trailing slash
    path('update-message-content', views.update_message_content, name='update-message-content'),
    path('delete-chat', views.delete_chat, name='delete-chat'),
    path('settings', views.settings, name='account-settings'),
    path('blogs', views.blogs, name='blog'),
    path('blog/<str:blog_slug>', views.blog_detail, name='blog-detail'),
    path('edit-connection-details', views.edit_connection_details, name='edit-connection-details'),
    path('test-connection', views.test_connection, name='test-connection'),
    #path('payment-portal', views.payment_portal, name='payment-portal'),
    path("payment-portal/", checkout_views.payment_portal, name="payment_portal"),

    path('privacy', views.privacy, name='privacy'),
    path('terms', views.terms, name='terms'),
    path('api/retell/start-call', retell_api.start_call, name='retell-start-call'),
    path('auth_che  ck', views.auth_check, name='auth-check'),  # Add auth check endpoint
    path('update-chat-name', views.update_chat_name, name='update-chat-name'),
    # path('api/whatsapp/webhook', whatsapp_api.webhook, name='whatsapp-webhook'),
    # path('api/whatsapp/configure', whatsapp_api.configure, name='whatsapp-configure'),
    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),
]
