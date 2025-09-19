# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, FileResponse, JsonResponse
from django.shortcuts import render, redirect
from django.template import loader
from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import os
from apps.auth import get_user_stripe_id_auth0
from apps import COMMON
from apps.authentication.models import CustomUser
from apps.auth_decorator import auth_decorator_func

from .models import Connection, Chat, Message, Blog
from .forms import ConnectionForm
from django.http import JsonResponse
from .util import generate_sql_query, create_connection_url, detect_visualization_type, create_visualization
from .tasks import run_sql_query, get_db_schema
import pandas as pd
from sqlalchemy import create_engine,text
from typing import Text
from django.core.serializers.json import DjangoJSONEncoder
import json
import stripe
import logging

stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_ENDPOINT_SECRET

# @login_required(login_url="login/")
# @auth_decorator_func
# def index(request):
#     if "auth0" not in request.session:
#         context = {'segment': 'index', 'is_logged_in': False}
#         html_template = loader.get_template('home/index.html')
#         return HttpResponse(html_template.render(context, request))
        
#     try:
#         auth0_id = request.session['auth0']['userinfo']['sub'].replace('auth0|', '')
#         user = CustomUser.objects.filter(auth0_id=auth0_id).first()
#         if not user:
#             return redirect('/login/')
#         return redirect('chat')
#     except Exception as e:
#         context = {'segment': 'index', 'is_logged_in': False}
#         html_template = loader.get_template('home/index.html')
#         return HttpResponse(html_template.render(context, request))

def index(request):
    context = {'segment': 'index', 'is_logged_in': False}
    
    # Check if user is authenticated via Auth0
    if "auth0" in request.session:
        try:
            auth0_id = request.session['auth0']['userinfo']['sub'].replace('auth0|', '')
            user = CustomUser.objects.filter(auth0_id=auth0_id).first()
            if user:
                context['is_logged_in'] = True
                return redirect('chat')  # Redirect authenticated users to chat
        except Exception as e:
            print(f"Error checking Auth0 session: {e}")
    
    # Render homepage for unauthenticated users
    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))

# @login_required(login_url="/login/")
@auth_decorator_func
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))

        segment, active_menu = get_segment( request )

        context['segment']     = segment
        context['active_menu'] = active_menu

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        #html_template = loader.get_template('home/page-404.html')
        #return HttpResponse(html_template.render(context, request))
        return redirect('home')

    except:
        return redirect('home')
        #html_template = loader.get_template('home/page-500.html')
        #return HttpResponse(html_template.render(context, request))

# Helper - Extract current page name from request
def get_segment( request ):

    try:

        segment     = request.path.split('/')[-1]
        active_menu = None

        if segment == '' or segment == 'index.html':
            segment     = 'index'
            active_menu = 'dashboard'

        if segment.startswith('dashboards-'):
            active_menu = 'dashboard'

        if segment.startswith('account-') or segment.startswith('users-') or segment.startswith('profile-') or segment.startswith('projects-'):
            active_menu = 'pages'

        if  segment.startswith('notifications') or segment.startswith('sweet-alerts') or segment.startswith('charts.html') or segment.startswith('widgets') or segment.startswith('pricing'):
            active_menu = 'pages'

        return segment, active_menu

    except:
        return 'index', 'dashboard'

def create_postgres_connection(request):
    print("create_postgres_connection")
    if request.method == 'POST':
        form = ConnectionForm(request.POST)
        print(form)
        if form.is_valid():
            connection = form.save(commit=False)
            connection.user = CustomUser.objects.filter(id=form.cleaned_data['users_id']).first()
            connection.save()
            #form.cleaned_data['user'] = CustomUser.objects.filter(id=form.cleaned_data['users_id']).first()    
            #form.save()
            #connection = form.save(commit=False)
            #connection.user_id = CustomUser.objects.filter(id=form.cleaned_data['user_id']).first()
            #connection.save()
            return redirect('connections.html')  # change this to your desired URL
    else:
        user_id = CustomUser.objects.filter(auth0_id=request.session['auth0']['userinfo']['sub'].replace('auth0|', '')).first().id
        print(user_id)
        if user_id:
            form = ConnectionForm(initial={'users_id': user_id})
        #form = ConnectionForm(initial={'user_id': request.session['auth0']['userinfo']['sub'].replace('auth0|', '')})
    html_template = loader.get_template('home/create-postgres-connection.html')
    context = {'form': form}
    
    return HttpResponse(html_template.render(context, request))

def connections(request):
    # user = CustomUser.objects.filter(auth0_id=request.session['auth0']['userinfo']['sub'].replace('auth0|', '')).first()
    auth0_id = request.session['auth0']['userinfo']['sub'].replace('auth0|', '')
    email = request.session['auth0']['userinfo']['email']
    user = CustomUser.objects.get(username=auth0_id, email=email)
    connections = Connection.objects.filter(user=user)
    print(connections)
    return render(request, 'home/connections.html', {'connections': connections})

@auth_decorator_func
def settings(request):
    # user = CustomUser.objects.filter(auth0_id=request.session['auth0']['userinfo']['sub'].replace('auth0|', '')).first()
    auth0_id = request.session['auth0']['userinfo']['sub'].replace('auth0|', '')
    email = request.session['auth0']['userinfo']['email']
    user = CustomUser.objects.get(username=auth0_id, email=email)
    connections = Connection.objects.filter(user=user)
    print(connections)
    return render(request, 'home/settings.html', {'connections': connections, 'user_id': user.id})


# @auth_decorator_func
# def chat(request, connection_id=None):
#     try:
#         auth0_id = request.session['auth0']['userinfo']['sub'].replace('auth0|', '')
#         email = request.session['auth0']['userinfo']['email']
#         user = CustomUser.objects.filter(username=auth0_id, email=email).first()

#         if not user:
#             return redirect('/login/')
#         stripe_customer_id = user.stripe_customer_id
#         if stripe_customer_id:
#             stripe.api_key = "sk_test_51H4rQIExPGKy6MgXTzuh72WSaLbxV95K1jB3RrwGZwGfRQPfzZK23XDbzRIIVJXQ3GLvDBjVH8kdEuNolAgmzMem00ODBddiWi"
#             subscriptions = stripe.Subscription.list(
#                                 customer=stripe_customer_id,
#                                 status='active',
#                                 limit=1
#                             )
             
#             if not subscriptions.data:
#                 return redirect('payment_portal')
#         print("sddg")
#         # chat_id = request.GET.get('chat_id')
#         # If user has no connections, show connections page with message
#         connection = Connection.objects.filter(user=user).first()
#         if not connection:
#             # Create a default connection (modify these values as needed)
#             connection = Connection.objects.create(
#                 user=user,
#                 name="Connection",
#                 host="unsql-postgres.postgres.database.azure.com",  # Replace with default or user-provided values
#                 port=5432,         # Default PostgreSQL port
#                 username="unsql_admin",  # Replace with default or user-provided values
#                 db_name="postgres",    # Replace with default or user-provided values
#                 db_type="postgres",
#                 password="OZpb3Bf4zoTslo"  # Replace with secure handling
#             )
#         # if not Connection.objects.filter(user=user).exists():
#         #     return render(request, 'home/connections.html', {
#         #         'message': 'Please create a connection to start chatting',
#         #         'connections': []
#         #     })

#         # If no chat_id provided, open the last chat
#         print(connection_id)
#         chat_id = request.GET.get('chat_id')
#         print(chat_id,'chatddd')
#         if not chat_id:
#             last_chat = Chat.objects.filter(user=user).order_by('-created_at').first()
#             if last_chat:
#                 return redirect(f'/chat/{last_chat.connection.id}/?chat_id={last_chat.id}')
#             else:
#                 # no chats yet → go to connections
#                 return redirect('connections')

#         # Otherwise load the requested chat
#         chat = Chat.objects.filter(id=chat_id, user=user).first()
#         if not chat:
#             return redirect('connections')

#         connection = chat.connection
#         messages = Message.objects.filter(chat=chat).order_by('order')

#         context = {
#             'segment': 'chat',
#             'chat': chat,
#             'chats': Chat.objects.filter(user=user).order_by('-created_at'),
#             'messages': messages,
#             'connection': connection,
#             'connection_id': connection.id
#         }
#         return render(request, 'home/chat.html', context)

#     except Exception as e:
#         import traceback
#         print(f"Error in chat view: {e}")
#         print(traceback.format_exc())
#         return redirect('connections')

@auth_decorator_func
def chat(request, connection_id=None):
    try:
        auth0_id = request.session['auth0']['userinfo']['sub'].replace('auth0|', '')
        email = request.session['auth0']['userinfo']['email']
        user = CustomUser.objects.filter(username=auth0_id, email=email).first()

        if not user:
            return redirect('/login/')

        # Create or get a connection
        connection = Connection.objects.filter(user=user).first()
        if not connection:
            connection = Connection.objects.create(
                user=user,
                name="Connection",
                host="unsql-postgres.postgres.database.azure.com",
                port=5432,
                username="unsql_admin",
                db_name="postgres",
                db_type="postgres",
                password="OZpb3Bf4zoTslo"
            )

        # Create a default chat if none exists
        chat_id = request.GET.get('chat_id')
        if not chat_id:
            last_chat = Chat.objects.filter(user=user).order_by('-created_at').first()
            if not last_chat:
                # Create a default chat
                last_chat = Chat.objects.create(
                    name="Default Chat",
                    user=user,
                    connection=connection
                )
            return redirect(f'/chat/{last_chat.connection.id}/?chat_id={last_chat.id}')

        # Load the requested chat
        chat = Chat.objects.filter(id=chat_id, user=user).first()
        if not chat:
            # Create a new chat if the requested one doesn't exist
            chat = Chat.objects.create(
                name="Default Chat",
                user=user,
                connection=connection
            )
            return redirect(f'/chat/{chat.connection.id}/?chat_id={chat.id}')

        messages = Message.objects.filter(chat=chat).order_by('order')

        context = {
            'segment': 'chat',
            'chat': chat,
            'chats': Chat.objects.filter(user=user).order_by('-created_at'),
            'messages': messages,
            'connection': connection,
            'connection_id': connection.id
        }
        return render(request, 'home/chat.html', context)

    except Exception as e:
        import traceback
        print(f"Error in chat view: {e}")
        print(traceback.format_exc())
        return redirect('chat')  # Redirect to chat instead of connections

def get_chat_messages(request):
    # Extract chat id from POST data
    
    chat_id = request.GET.get('chat_id')
    connection_id = request.GET.get('connection_id')
    if not chat_id:
        return JsonResponse({'error': 'Missing chat_id parameter.'}, status=400)
    
    # Fetch chat object
    try:
        chat = Chat.objects.get(id=chat_id)#, connection=connection_id)
    except Chat.DoesNotExist:
        return JsonResponse({'error': 'Chat not found.'}, status=404)

    # Fetch the messages for this chat
    messages = Message.objects.filter(chat=chat).order_by('order')
    
    # Prepare response data
    response_data = {
        'chat_name': chat.name,
        'messages': [
            {
                'content': message.message,
                'user': message.user.email, # Use the CustomUser email as the user identifier
                'timestamp': message.created_at.strftime('%Y-%m-%d %H:%M:%S'),  # Format datetime object as string
                'system_message': message.system_message,
                'id': message.id,
                'connection_id': message.chat.connection.id,
                'head_data': message.head_data,
                'english_query': message.english_query,
            }
            for message in messages
        ]
    }
    
    return JsonResponse(response_data)


@login_required
def edit_connection_details(request):
    if request.method == 'POST':
        try:
            connection_id = request.POST.get('connection_id')
            connection = Connection.objects.get(id=connection_id, user=request.user)
            
            connection.name = request.POST.get('name', connection.name)
            connection.host = request.POST.get('host', connection.host)
            connection.port = request.POST.get('port', connection.port)
            connection.username = request.POST.get('username', connection.username)
            connection.db_name = request.POST.get('db_name', connection.db_name)
            connection.db_type = request.POST.get('db_type', connection.db_type)
            
            # Only update password if provided
            new_password = request.POST.get('password')
            if new_password:
                connection.set_password(new_password)
            
            connection.save()
            return JsonResponse({'success': True})
            
        except Connection.DoesNotExist:
            return JsonResponse({'error': 'Connection not found'}, status=404)
        except Exception as e:
            logger.error(f"Error updating connection: {str(e)}", exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@auth_decorator_func
def settings(request):
    # user = CustomUser.objects.filter(auth0_id=request.session['auth0']['userinfo']['sub'].replace('auth0|', '')).first()
    auth0_id = request.session['auth0']['userinfo']['sub'].replace('auth0|', '')
    email = request.session['auth0']['userinfo']['email']
    user = CustomUser.objects.get(username=auth0_id, email=email)
    connections = Connection.objects.filter(user=user)
    print(connections)
    return render(request, 'home/settings.html', {'connections': connections, 'user_id': user.id})

@csrf_exempt
@auth_decorator_func
# def new_message(request):
#     import logging
#     logger = logging.getLogger(__name__)
    
#     # # Log the request details
#     # logger.info(f"[new_message] Request method: {request.method}")
#     # logger.info(f"[new_message] Request POST data: {request.POST}")
#     # logger.info(f"[new_message] Request headers: {request.headers}")
    
#     if request.method == 'POST':
#         try:
#             # Extract message data
#             message_text = request.POST.get('message', '')
#             user_id = request.POST.get('user_id', None)
#             chat_id = request.POST.get('chat_id', None)
            
#             # logger.info(f"[new_message] Received request - message: {message_text}, user_id: {user_id}, chat_id: {chat_id}")
            
#             # Validate inputs
#             if not message_text:
#                 logger.error("[new_message] No message text provided")
#                 return JsonResponse({"error": "Message text is required"}, status=400)
                
#             if not chat_id:
#                 logger.error("[new_message] No chat_id provided")
#                 return JsonResponse({"error": "Chat ID is required"}, status=400)
            
#             # Get chat and connection
#             chat = Chat.objects.filter(id=chat_id).first()
#             if not chat:
#                 logger.error(f"[new_message] Chat not found: {chat_id}")
#                 return JsonResponse({"error": "Chat not found"}, status=404)
                
#             connection = chat.connection
#             if not connection:
#                 logger.error(f"[new_message] No connection associated with chat: {chat_id}")
#                 return JsonResponse({"error": "No connection found for this chat"}, status=404)
            
#             # Get or create user
#             # user = CustomUser.objects.filter(auth0_id=request.session['auth0']['userinfo']['sub'].replace('auth0|', '')).first()
#             auth0_id = request.session['auth0']['userinfo']['sub'].replace('auth0|', '')
#             email = request.session['auth0']['userinfo']['email']
#             user = CustomUser.objects.get(username=auth0_id, email=email)
#             if not user:
#                 logger.error("[new_message] User not found")
#                 return JsonResponse({"error": "User not found"}, status=404)
            
#             # Create user message
#             user_message = Message.objects.create(
#                 chat=chat,
#                 user=user,
#                 message=message_text,
#                 system_message=False
#             )
            
#             # Get SQL query from message
#             # print(user_message)
#             sql_query = generate_sql_query(message_text, connection.id, user_message.id)
#             # print(sql_query,"sql")

#             if sql_query.startswith("Error:"):
#                 logger.error(f"[new_message] SQL generation failed: {sql_query}")
#                 return JsonResponse({
#                     'success': True,
#                     'messages': [
#                         {
#                             'id': user_message.id,
#                             'message': user_message.message,
#                             'timestamp': user_message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
#                             'system_message': user_message.system_message,
#                             'sql': sql_query,  # Pass the error message as sql
#                             'head_data': sql_query  # Pass the error message as head_data
#                         }
#                     ]
#                 })

#             if sql_query is None:
#                 logger.error(f"[new_message] SQL query generation returned None for message: {message_text}")
#                 return JsonResponse({
#                     "error": "Unable to generate SQL query. The input may be invalid or not supported.",
#                     "message_id": user_message.id,
#                     "timestamp": user_message.created_at.strftime('%Y-%m-%d %H:%M:%S')
#                 }, status=400)

#             if not sql_query.strip():
#                 logger.error(f"[new_message] Generated SQL query is empty for message: {message_text}")
#                 return JsonResponse({
#                     "error": "Generated SQL query is empty.",
#                     "message_id": user_message.id,
#                     "timestamp": user_message.created_at.strftime('%Y-%m-%d %H:%M:%S')
#                 }, status=400)
            
#             print("==================================================")
            
#             print(sql_query)
#             # Create assistant message with SQL
#             assistant_message = Message.objects.create(
#                 chat=chat,
#                 user=user,
#                 message=sql_query,
#                 system_message=True,
#                 sql=sql_query
#             )
            
#             # Execute SQL query
#             try:

#                 result = run_sql_query(create_connection_url(connection.id), sql_query)
#                 print("result data",result)
#                 assistant_message.head_data = json.dumps(result["response_data"])
#                 assistant_message.save()
                
#                 return JsonResponse({
#                     'success': True,
#                     'messages': [
#                         {
#                             'id': user_message.id,
#                             'message': user_message.message,
#                             'timestamp': user_message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
#                             'system_message': user_message.system_message,
#                             'sql': None,
#                             'head_data': None
#                         },
#                         {
#                             'id': assistant_message.id,
#                             'message': assistant_message.message,
#                             'sql': assistant_message.sql,
#                             'head_data': None,  # Don't include data until SQL is run
#                             'timestamp': assistant_message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
#                             'system_message': assistant_message.system_message
#                         }
#                     ]
#                 })
                
#             except Exception as e:
#                 logger.error(f"[new_message] Error executing SQL: {e}")
#                 return JsonResponse({"error": f"Error executing SQL: {str(e)}"}, status=400)
                
#         except Exception as e:
#             logger.error(f"[new_message] Error: {e}")
#             return JsonResponse({"error": str(e)}, status=500)
            
#     return JsonResponse({"error": "Invalid request method"}, status=405)

def new_message(request):
    import logging
    logger = logging.getLogger(__name__)
    
    if request.method == 'POST':
        try:
            # Extract message data
            message_text = request.POST.get('message', '')
            user_id = request.POST.get('user_id', None)
            chat_id = request.POST.get('chat_id', None)
            
            # Validate inputs
            if not message_text:
                logger.error("[new_message] No message text provided")
                return JsonResponse({"error": "Message text is required"}, status=400)
                
            if not chat_id:
                logger.error("[new_message] No chat_id provided")
                return JsonResponse({"error": "Chat ID is required"}, status=400)
            
            # Get chat and connection
            chat = Chat.objects.filter(id=chat_id).first()
            if not chat:
                logger.error(f"[new_message] Chat not found: {chat_id}")
                return JsonResponse({"error": "Chat not found"}, status=404)
                
            connection = chat.connection
            if not connection:
                logger.error(f"[new_message] No connection associated with chat: {chat_id}")
                return JsonResponse({"error": "No connection found for this chat"}, status=404)
            
            # Get or create user
            auth0_id = request.session['auth0']['userinfo']['sub'].replace('auth0|', '')
            email = request.session['auth0']['userinfo']['email']
            user = CustomUser.objects.get(username=auth0_id, email=email)
            if not user:
                logger.error("[new_message] User not found")
                return JsonResponse({"error": "User not found"}, status=404)
            
            # Create user message
            user_message = Message.objects.create(
                chat=chat,
                user=user,
                message=message_text,
                system_message=False
            )
            
            # Get SQL query from message
            sql_query = generate_sql_query(message_text, connection.id, user_message.id)
            
            # Check for error from generate_sql_query
            error_message = None
            if isinstance(sql_query, dict) and sql_query.get('Error'):
                error_message = sql_query.get('Error')
            elif isinstance(sql_query, str) and sql_query.startswith("Error:"):
                error_message = sql_query
            elif sql_query is None:
                error_message = "Unable to generate SQL query. The input may be invalid or not supported."
            elif not sql_query.strip():
                error_message = "Generated SQL query is empty."
            
            if error_message:
                logger.error(f"[new_message] SQL generation failed: {error_message}")
                # Create assistant message for error
                assistant_message = Message.objects.create(
                    chat=chat,
                    user=user,
                    message=error_message,
                    system_message=True,
                    sql=error_message
                )
                return JsonResponse({
                    'success': True,
                    'messages': [
                        {
                            'id': user_message.id,
                            'message': user_message.message,
                            'timestamp': user_message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                            'system_message': user_message.system_message,
                            'sql': None,
                            'head_data': None
                        },
                        {
                            'id': assistant_message.id,
                            'message': assistant_message.message,
                            'timestamp': assistant_message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                            'system_message': assistant_message.system_message,
                            'sql': assistant_message.sql,
                            'head_data': None
                        }
                    ]
                })
            
            # Create assistant message with SQL
            assistant_message = Message.objects.create(
                chat=chat,
                user=user,
                message=sql_query,
                system_message=True,
                sql=sql_query
            )
            
            # Execute SQL query
            try:
                result = run_sql_query(create_connection_url(connection.id), sql_query)
                assistant_message.head_data = json.dumps(result["response_data"])
                assistant_message.save()
                
                return JsonResponse({
                    'success': True,
                    'messages': [
                        {
                            'id': user_message.id,
                            'message': user_message.message,
                            'timestamp': user_message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                            'system_message': user_message.system_message,
                            'sql': None,
                            'head_data': None
                        },
                        {
                            'id': assistant_message.id,
                            'message': assistant_message.message,
                            'sql': assistant_message.sql,
                            'head_data': result["response_data"],
                            'timestamp': assistant_message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                            'system_message': assistant_message.system_message
                        }
                    ]
                })
                
            except Exception as e:
                logger.error(f"[new_message] Error executing SQL: {e}")
                # Create assistant message for SQL execution error
                error_message = f"Error executing SQL: {str(e)}"
                assistant_message = Message.objects.create(
                    chat=chat,
                    user=user,
                    message=error_message,
                    system_message=True,
                    sql=error_message
                )
                return JsonResponse({
                    'success': True,
                    'messages': [
                        {
                            'id': user_message.id,
                            'message': user_message.message,
                            'timestamp': user_message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                            'system_message': user_message.system_message,
                            'sql': None,
                            'head_data': None
                        },
                        {
                            'id': assistant_message.id,
                            'message': assistant_message.message,
                            'sql': assistant_message.sql,
                            'head_data': None,
                            'timestamp': assistant_message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                            'system_message': assistant_message.system_message
                        }
                    ]
                })
                
        except Exception as e:
            logger.error(f"[new_message] Error: {e}")
            return JsonResponse({"error": str(e)}, status=500)
            
    return JsonResponse({"error": "Invalid request method"}, status=405)

def get_chat_messages(request):
    # Extract chat id from POST data
    
    chat_id = request.GET.get('chat_id')
    connection_id = request.GET.get('connection_id')
    if not chat_id:
        return JsonResponse({'error': 'Missing chat_id parameter.'}, status=400)
    
    # Fetch chat object
    try:
        chat = Chat.objects.get(id=chat_id)#, connection=connection_id)
    except Chat.DoesNotExist:
        return JsonResponse({'error': 'Chat not found.'}, status=404)

    # Fetch the messages for this chat
    messages = Message.objects.filter(chat=chat).order_by('order')
    
    # Prepare response data
    response_data = {
        'chat_name': chat.name,
        'messages': [
            {
                'content': message.message,
                'user': message.user.email, # Use the CustomUser email as the user identifier
                'timestamp': message.created_at.strftime('%Y-%m-%d %H:%M:%S'),  # Format datetime object as string
                'system_message': message.system_message,
                'id': message.id,
                'connection_id': message.chat.connection.id,
                'head_data': message.head_data,
                'english_query': message.english_query,
            }
            for message in messages
        ]
    }
    
    return JsonResponse(response_data)


def delete_chat(request):
    # Extract chat id from POST data
    chat_id = request.GET.get('chat_id')
    if not chat_id:
        return JsonResponse({'error': 'Missing chat_id parameter.'}, status=400)
    
    # Fetch chat object
    try:
        chat = Chat.objects.get(id=chat_id)
    except Chat.DoesNotExist:
        return JsonResponse({'error': 'Chat not found.'}, status=404)
    
    # Delete the chat
    chat.delete()
    
    return JsonResponse({'success': True})

def update_message_content(request):
    # Extract chat id from POST data
    message_id = request.GET.get('message_id')
    new_content = request.GET.get('new_content')
    message_id = int(message_id)
    
    message = Message.objects.filter(id=message_id).first()

    if not message:
        return JsonResponse({'error': 'Missing message parameter.'}, status=400)
    
    message.message = new_content
    message.save()
    
    return JsonResponse({'success': True})

def generate_sample_data(request):
    # Extract chat id from POST data
    message_id = request.GET.get('message_id')
    
    #connection_id = request.GET.get('connection_id')
    message_id = int(message_id)
    #connection_id = int(connection_id)
    
    message = Message.objects.filter(id=message_id).first()
    connection_id = message.chat.connection.id
    if not message:
        return JsonResponse({'error': 'Missing message parameter.'}, status=400)
    
    try:
        connection_url = create_connection_url(connection_id)
    except Connection.DoesNotExist:
        return JsonResponse({'error': 'Connection not found.'}, status=404)
    
    try:
        results = run_sql_query(connection_url, message.message)
        
    except Exception as e:
        print(e)
        return JsonResponse({'error': str(e)}, status=400)
    
    try:
        response_data = results["response_data"]
        affected_rows = results["affected_rows"]
        try:
            error = results["error"]
        except:
            error = False
        if error==True:
            return JsonResponse({'error': affected_rows}, status=400)
        try:
            success = results["success"]
        except:
            success = False

        if success==True:
            return JsonResponse({'error': "Success. Query doesn't return any results"}, status=400)
        
        try:
            # Convert JSON string to list of dictionaries for Django template
            response_data = json.loads(response_data)
            
            message.head_data = json.dumps(response_data, cls=DjangoJSONEncoder)
            
            #message.head_data = response_data
            message.save()
        except Exception as y:
            print("y-error: " + str(y))
            return(JsonResponse({'error': affected_rows}, status=400))
        
        return JsonResponse({'success': True, 'affected_rows': affected_rows})
        #return JsonResponse(response_data, safe=False)
    except Exception as e:
        print(e)
        return JsonResponse({'error': str(e)}, status=400)

@auth_decorator_func
def visualize(request):
    logger = logging.getLogger(__name__)
    logger.info("Starting visualization view")
    logger.info(f"Request method: {request.method}")
    logger.info(f"Request path: {request.path}")
    logger.info(f"Request GET params: {request.GET}")
    
    try:
        try:
            logger.info("Getting user from session")
            logger.info(f"Session data: {request.session.get('auth0', {})}")
            # user = CustomUser.objects.filter(auth0_id=request.session['auth0']['userinfo']['sub'].replace('auth0|', '')).first()
            auth0_id = request.session['auth0']['userinfo']['sub'].replace('auth0|', '')
            email = request.session['auth0']['userinfo']['email']
            user = CustomUser.objects.get(username=auth0_id, email=email)
            logger.info(f"Found user: {user}")
            if not user:
                logger.error("User not found")
                return redirect('/login/')
        except Exception as e:
            logger.error(f"Auth error in visualize: {e}", exc_info=True)
            return redirect('/login/')
            
        message_id = request.GET.get('message_id')
        print('message id',message_id)
        logger.info(f"Got message_id: {message_id}")
        if not message_id:
            logger.error("No message_id provided")
            return redirect('chat')
            
        viz_type = request.GET.get('viz_type')
        logger.info(f"Visualizing message {message_id} with type {viz_type}")
        
        # Log the query being made
        logger.info(f"Querying Message with id={message_id} for user {user.id}")
        message = Message.objects.filter(
            id=message_id,
            chat__user=user  # Check if message belongs to user's chat
        ).first()
        logger.info(f"Found message: {message}")
        if not message:
            logger.error(f"Message {message_id} not found in user's chats")
            return redirect('chat')

        # Get the SQL results from head_data
        logger.info(f"Message head_data: {message.head_data}")
        if not message.head_data:
            logger.error(f"No head_data for message {message_id}")
            return redirect(f'/chat/{message.chat.connection.id}/?chat_id={message.chat.id}')
            
        try:
            result = json.loads(message.head_data)
            logger.info(f"Parsed head_data: {result[:2] if result else []}")  # Only show first 2 items
            if not result:
                logger.error(f"Empty result data for message {message_id}")
                return redirect(f'/chat/{message.chat.connection.id}/?chat_id={message.chat.id}')
            print('result',result)
            columns = list(result[0].keys()) if result else []
            logger.info(f"Found columns: {columns}")
            
            # Convert the result to a pandas DataFrame
            df = pd.DataFrame(result, columns=columns)
            logger.info(f"Created DataFrame with shape: {df.shape}")
            
            # Detect the visualization type and create the visualization
            if viz_type:
                visualization_type = viz_type
            else:
                visualization_type = detect_visualization_type(df)
            logger.info(f"Using visualization type: {visualization_type}")
                
            # Get the user's question from the previous message
            previous_message = Message.objects.filter(chat=message.chat, order=message.order-1).first()
            previous_text = previous_message.message if previous_message else ""
            logger.info(f"Previous message text: {previous_text}")
            
            visualization_html = create_visualization(df, visualization_type, previous_text)
            logger.info("Created visualization HTML")

            # Format table data
            table_data = [list(item.values()) for item in result]
            logger.info(f"Formatted table data with {len(table_data)} rows")

            context = {
                'sql_query': message.message,
                'visualization_html': visualization_html,
                'table_data': table_data,
                'columns': columns,
                'message': message,
                'segment': 'visualization',
                'chat': message.chat,
                'connection': message.chat.connection
            }
            
            logger.info(f"Context prepared: {context.keys()}")
            logger.info("Rendering visualization template")
            return render(request, 'home/vizualization.html', context)
            
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {e}", exc_info=True)
            return redirect(f'/chat/{message.chat.connection.id}/?chat_id={message.chat.id}')
        except ValueError as e:
            logger.error(f"Error creating visualization: {e}", exc_info=True)
            return redirect(f'/chat/{message.chat.connection.id}/?chat_id={message.chat.id}')
        except Exception as e:
            logger.error(f"Error processing visualization: {e}", exc_info=True)
            return redirect(f'/chat/{message.chat.connection.id}/?chat_id={message.chat.id}')
            
    except Exception as e:
        logger.error(f"Visualization error: {e}", exc_info=True)
        # If we can't get the chat info, redirect to the main chat page
        return redirect('chat')

@auth_decorator_func
def new_chat(request):
    import logging
    logger = logging.getLogger(__name__)
    
    # Only handle POST requests
    if request.method == 'POST':
        chat_name = request.POST.get('name', 'New Chat')
        user_id = request.POST.get('user_id')
        connection_id = request.POST.get('connection_id')
        
        logger.info(f"[new_chat] Creating chat - name: {chat_name}, user_id: {user_id}, connection_id: {connection_id}")

        try:
            # Get user and connection
            # user = CustomUser.objects.filter(auth0_id=request.session['auth0']['userinfo']['sub'].replace('auth0|', '')).first()
            auth0_id = request.session['auth0']['userinfo']['sub'].replace('auth0|', '')
            email = request.session['auth0']['userinfo']['email']
            user = CustomUser.objects.get(username=auth0_id, email=email)
            if not user:
                logger.error(f"[new_chat] User not found in session")
                return JsonResponse({'error': 'User not found'}, status=404)
                
            connection = Connection.objects.filter(id=connection_id, user=user).first()
            if not connection:
                logger.error(f"[new_chat] Connection not found - connection_id: {connection_id}")
                return JsonResponse({'error': 'Connection not found'}, status=404)
            
            # Create new chat
            chat = Chat.objects.create(
                name=chat_name,
                user=user,
                connection=connection
            )
            logger.info(f"[new_chat] Created chat with id: {chat.id}")
            
            return JsonResponse({
                'success': True,
                'chat_id': chat.id,
                'connection_id': connection.id
            })
            
        except Exception as e:
            logger.error(f"[new_chat] Error creating chat: {e}")
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Invalid request method'}, status=400)

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import logging

logger = logging.getLogger(__name__)

@login_required
def test_connection(request):
    if not request.is_ajax():
        return JsonResponse({'error': 'AJAX request required'}, status=400)
        
    try:
        db_name = request.GET.get('db_name')
        db_host = request.GET.get('db_host')
        db_port = request.GET.get('db_port')
        db_user = request.GET.get('db_user')
        db_password = request.GET.get('db_password')
        db_type = request.GET.get('db_type', 'postgres')  # Default to postgres for backward compatibility

        if not all([db_name, db_host, db_port, db_user, db_password]):
            return JsonResponse({'error': 'Missing required parameters'})

        connection_url = create_connection_url(
            db_name=db_name,
            db_host=db_host,
            db_port=db_port,
            db_user=db_user,
            db_password=db_password,
            db_type=db_type
        )

        engine = create_engine(connection_url)
        with engine.connect() as connection:
            connection.execute(text('SELECT 1'))
            return JsonResponse({'success': True})

    except Exception as e:
        logger.error(f"Error testing connection: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)})

def privacy(request):
    return render(request, 'home/privacy.html')

def terms(request):
    return render(request, 'home/terms.html')
    
def payment_portal(request):
    try:
        # user = CustomUser.objects.filter(auth0_id=request.session['auth0']['userinfo']['sub'].replace('auth0|', '')).first()
        auth0_id = request.session['auth0']['userinfo']['sub'].replace('auth0|', '')
        email = request.session['auth0']['userinfo']['email']
        user = CustomUser.objects.get(username=auth0_id, email=email)
        stripe_customer_id = get_user_stripe_id_auth0(request.session['auth0']['userinfo']['sub'])
        
        print("DEBUG: Found stripe ID in database:", stripe_customer_id)
        print("user", user)
        print("stripe_customer_id", stripe_customer_id)
        
        user.stripe_customer_id = stripe_customer_id
        user.save()

        return redirect('https://billing.stripe.com/p/login/test_5kA3fq2X57Op0AEbII')
            
    except Exception as e:
        print("ERROR:", str(e))
        return redirect('/settings?error=payment_portal_error')
    
def blogs(request):
    try:
        auth0_id = request.session['auth0']['userinfo']['sub'].replace('auth0|', '')
    except:
        context = {'is_logged_in': False}
        #return render(request, 'home/blog.html', context)
        return redirect('https://blog.unsql.ai/')
    
    logged_in = CustomUser.objects.filter(auth0_id=auth0_id).exists()
    context = {'is_logged_in': logged_in}
    #return render(request, 'home/blog.html', context)
    return redirect('https://blog.unsql.ai/')

def blog_detail(request, blog_slug):
    blog = Blog.objects.filter(slug=blog_slug).first()
    if not blog:
        return redirect('blogs')
    context = {
        'blog': blog,
    }
    return render(request, 'home/blog_detail.html', context)

def auth_check(request):
    """
    Endpoint for nginx auth_request to check if user is authenticated and has subscription
    """
    if "auth0" not in request.session:
        return HttpResponse(status=401)
        
    token = request.session['auth0']
    stripe_id = get_user_stripe_id_auth0(token['userinfo']['sub'])
    
    if isinstance(stripe_id, dict) and stripe_id.get('status') == 'failed':
        return HttpResponse(status=403)
    
    if stripe_id:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            subscription = stripe.Subscription.list(
                customer=stripe_id,
                status='active',
                limit=1
            )
            if subscription.data:
                return HttpResponse(status=200)
        except stripe.error.StripeError:
            pass
            
    return HttpResponse(status=403)

@csrf_exempt
@auth_decorator_func
def execute_sql(request):
    import logging
    import json
    import psycopg2
    from psycopg2.extras import RealDictCursor
    
    logger = logging.getLogger(__name__)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    
    try:
        # Extract data
        data = json.loads(request.body)
        sql_query = data.get('sql_query')
        chat_id = data.get('chat_id')
        
        if not sql_query or not chat_id:
            return JsonResponse({'error': 'SQL query and chat ID are required'}, status=400)
        
        # Get chat and connection details
        chat = Chat.objects.get(id=chat_id)
        connection = chat.connection
        
        # Get user
        # user = CustomUser.objects.filter(auth0_id=request.session['auth0']['userinfo']['sub'].replace('auth0|', '')).first()
        auth0_id = request.session['auth0']['userinfo']['sub'].replace('auth0|', '')
        email = request.session['auth0']['userinfo']['email']
        user = CustomUser.objects.get(username=auth0_id, email=email)
        
        if not user:
            return JsonResponse({'error': 'User not found'}, status=404)
        
        # Connect to database
        conn = psycopg2.connect(
            dbname=connection.db_name,
            user=connection.username,
            password=connection.get_password(),
            host=connection.host,
            port=connection.port
        )
        
        # Execute query
        with conn.cursor() as cur:
            cur.execute(sql_query)
            columns = [desc[0] for desc in cur.description]
            results = [dict(zip(columns, row)) for row in cur.fetchall()]
            
            # Store results in message
            message = Message.objects.create(
                chat=chat,
                user=user,
                message=sql_query,
                system_message=True,
                head_data=json.dumps(results)
            )

        return JsonResponse({
            'columns': columns,
            'results': results,
            'message_id': message.id
        })
        
    except Chat.DoesNotExist:
        return JsonResponse({'error': 'Chat not found'}, status=404)
    except psycopg2.Error as e:
        logger.error(f"Database error: {str(e)}")
        return JsonResponse({'error': f'Database error: {str(e)}'}, status=500)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@auth_decorator_func
def update_chat_name(request):
    import logging
    logger = logging.getLogger(__name__)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
        
    try:
        chat_id = request.POST.get('chat_id')
        new_name = request.POST.get('name')
        
        logger.info(f"Updating chat name - chat_id: {chat_id}, new_name: {new_name}")
        
        if not chat_id or not new_name:
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        # Get the user from session
        # user = CustomUser.objects.filter(auth0_id=request.session['auth0']['userinfo']['sub'].replace('auth0|', '')).first()
        auth0_id = request.session['auth0']['userinfo']['sub'].replace('auth0|', '')
        email = request.session['auth0']['userinfo']['email']
        user = CustomUser.objects.get(username=auth0_id, email=email)
        
        if not user:
            logger.error("User not found")
            return JsonResponse({'error': 'User not found'}, status=404)
        
        # Get and update the chat
        chat = Chat.objects.filter(id=chat_id, user=user).first()
        if not chat:
            logger.error(f"Chat {chat_id} not found for user {user.id}")
            return JsonResponse({'error': 'Chat not found'}, status=404)
        
        chat.name = new_name
        chat.save()
        logger.info(f"Successfully updated chat {chat_id} name to '{new_name}'")
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        logger.error(f"Error updating chat name: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)