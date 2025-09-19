from openai import OpenAI
from django.http import JsonResponse
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from .models import Connection, Message, Chat
import requests
from .tasks import get_db_schema, run_sql_query
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


client = OpenAI(api_key="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")


def query(query, messages=None):
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # logger.info(f"[query] Starting OpenAI query")
        # logger.info(f"[query] Query: {query}")
        # logger.info(f"[query] Messages: {messages}")
        
        if messages:
            messages.append(
                {
                    "role": "user",
                    "content": query,
                }
            )
            # logger.info(f"[query] Calling OpenAI with messages: {messages}")
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
            )
        else:
            # logger.info("[query] No messages provided, using simple query")
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": query,
                    }
                ]
            )
        
        result = response.choices[0].message.content.strip()
        # logger.info(f"[query] OpenAI response: {result}")
        return result
        
    except Exception as e:
        logger.error(f"[query] Error calling OpenAI: {str(e)}", exc_info=True)
        return e

# def generate_sql_query(user_question, connection_id, message_id=None, error=None, past_sql=None):
#     import logging
#     logger = logging.getLogger(__name__)
    
#     try:
#         message_list = []
#         # logger.info(f"[generate_sql_query] Starting with user_question: {user_question}, connection_id: {connection_id}")
        
#         if message_id:
#             # logger.info(f"[generate_sql_query] Processing message_id: {message_id}")
            
#             # Get chat and messages
#             message = Message.objects.filter(id=message_id).first()
#             if not message:
#                 # logger.error(f"[generate_sql_query] Message not found: {message_id}")
#                 return "Error: Message not found"
                
#             chat_id = message.chat.id
#             messages = Message.objects.filter(chat_id=chat_id).order_by("-created_at")[:5]
#             # logger.info(f"[generate_sql_query] Found {len(messages)} previous messages")
            
#             # Get connection
#             connection = Connection.objects.filter(id=connection_id).first()
#             if not connection:
#                 logger.error(f"[generate_sql_query] Connection not found: {connection_id}")
#                 return "Error: Database connection not found"
                
#             # Get schema
#             # logger.info(f"[generate_sql_query] Getting schema for connection {connection_id}")
#             db_metadata = analyze_db_schema(connection_id)
#             db_type = connection.db_type
#             # Build message list
#             message_list.append(
#                 {
#                     "role": "system",
#                     "content": f"The database schema is: {str(db_metadata)}"
#                 }
#             )
#             message_list.append(
#                 {
#                     "role": "system",
#                     "content": f"You are an elite {db_type} programmer. You are part of an automated system, and you need to respond ONLY with code."
#                 }
#             )
            
#             # Add chat history
#             for msg in messages:
#                 if msg.system_message:
#                     message_list.append(
#                         {
#                             "role": "assistant",
#                             "content": msg.message,
#                         }
#                     )
#                 else:
#                     message_list.append(
#                         {
#                             "role": "user",
#                             "content": msg.message,
#                         }
#                     )
#             logger.info(f"[generate_sql_query] Built message list with {len(message_list)} messages")
            
#         else:
#             # If no message_id, just use a simple system prompt
#             logger.info("[generate_sql_query] No message_id provided, using simple prompt")
            
#             # Get connection
#             connection = Connection.objects.filter(id=connection_id).first()
#             if not connection:
#                 logger.error(f"[generate_sql_query] Connection not found: {connection_id}")
#                 return "Error: Database connection not found"
                
#             # Get schema
#             logger.info(f"[generate_sql_query] Getting schema for connection {connection_id}")
#             db_metadata = analyze_db_schema(connection_id)
#             db_type = connection.db_type
            
#             # logger.info(f"[generate_sql_query] Got db_metadata: {db_metadata}")
#             # logger.info(f"[generate_sql_query] Database type: {db_type}")
            
#             # Build message list
#             message_list.append(
#                 {
#                     "role": "system",
#                     "content": f"The database schema is: {str(db_metadata)}"
#                 }
#             )
#             message_list.append(
#                 {
#                     "role": "system",
#                     "content": f"You are an elite {db_type} programmer. You are part of an automated system, and you need to respond ONLY with code."
#                 }
#             )

#         # Prepare prompt
#         print("error-message", error)
#         if error:
#             prompt = user_question + "\n" + error
#             logger.info(f"[generate_sql_query] Using error prompt: {prompt}")
#         else:
#             prompt = user_question
#             logger.info(f"[generate_sql_query] Using standard prompt: {prompt}")

#         # Call OpenAI
#         # logger.info("[generate_sql_query] Calling OpenAI query function")
#         response = query(prompt, message_list)
#         # logger.info(f"[generate_sql_query] Got response: {response}")
        
#         if isinstance(response, Exception):
#             logger.error(f"[generate_sql_query] Query returned error: {str(response)}")
#             return f"Error generating SQL: {str(response)}"
            
#         return response
        
#     except Exception as e:
#         logger.error(f"[generate_sql_query] Unexpected error: {str(e)}", exc_info=True)
#         return f"Error: {str(e)}"

def generate_sql_query(user_question, connection_id, message_id=None, error=None, past_sql=None):
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Validate input
        if not user_question or user_question.lower().strip() in ["hey", "hello", "hi"]:
            logger.error(f"[generate_sql_query] Invalid or vague user_question: {user_question}")
            return {"Error":"Input is too vague or invalid for SQL generation"}

        message_list = []
        logger.info(f"[generate_sql_query] Starting with user_question: {user_question}, connection_id: {connection_id}")
        
        if message_id:
            logger.info(f"[generate_sql_query] Processing message_id: {message_id}")
            
            # Get chat and messages
            message = Message.objects.filter(id=message_id).first()
            if not message:
                logger.error(f"[generate_sql_query] Message not found: {message_id}")
                return "Error: Message not found"
                
            chat_id = message.chat.id
            messages = Message.objects.filter(chat_id=chat_id).order_by("-created_at")[:5]
            logger.info(f"[generate_sql_query] Found {len(messages)} previous messages")
            
            # Get connection
            connection = Connection.objects.filter(id=connection_id).first()
            if not connection:
                logger.error(f"[generate_sql_query] Connection not found: {connection_id}")
                return "Error: Database connection not found"
                
            # Get schema
            logger.info(f"[generate_sql_query] Getting schema for connection {connection_id}")
            db_metadata = analyze_db_schema(connection_id)
            db_type = connection.db_type
            logger.info(f"[generate_sql_query] Database type: {db_type}, Schema: {db_metadata}")
            
            # Build message list
            message_list.append(
                {
                    "role": "system",
                    "content": (
                        f"You are an elite {db_type} programmer. The database schema is: {str(db_metadata)}. "
                        "Respond ONLY with valid SQL code. If the user input is vague or cannot be converted to SQL, "
                        "return 'Error: Cannot generate SQL for this input'."
                    )
                }
            )
            
            # Add chat history
            for msg in messages:
                if msg.system_message:
                    message_list.append(
                        {
                            "role": "assistant",
                            "content": msg.message,
                        }
                    )
                else:
                    message_list.append(
                        {
                            "role": "user",
                            "content": msg.message,
                        }
                    )
            logger.info(f"[generate_sql_query] Built message list with {len(message_list)} messages")
            
        else:
            logger.info("[generate_sql_query] No message_id provided, using simple prompt")
            
            # Get connection
            connection = Connection.objects.filter(id=connection_id).first()
            if not connection:
                logger.error(f"[generate_sql_query] Connection not found: {connection_id}")
                return "Error: Database connection not found"
                
            # Get schema
            logger.info(f"[generate_sql_query] Getting schema for connection {connection_id}")
            db_metadata = analyze_db_schema(connection_id)
            db_type = connection.db_type
            logger.info(f"[generate_sql_query] Database type: {db_type}, Schema: {db_metadata}")
            
            # Build message list
            message_list.append(
                {
                    "role": "system",
                    "content": (
                        f"You are an elite {db_type} programmer. The database schema is: {str(db_metadata)}. "
                        "Respond ONLY with valid SQL code. If the user input is vague or cannot be converted to SQL, "
                        "return 'Error: Cannot generate SQL for this input'."
                    )
                }
            )

        # Prepare prompt
        if error:
            prompt = f"{user_question}\nPrevious error: {error}"
            logger.info(f"[generate_sql_query] Using error prompt: {prompt}")
        else:
            prompt = user_question
            logger.info(f"[generate_sql_query] Using standard prompt: {prompt}")

        # Call OpenAI
        logger.info("[generate_sql_query] Calling OpenAI query function")
        response = query(prompt, message_list)
        logger.info(f"[generate_sql_query] Raw response: {response}")
        
        if isinstance(response, Exception):
            logger.error(f"[generate_sql_query] Query returned error: {str(response)}")
            return f"Error generating SQL: {str(response)}"
            
        # Clean and validate response
        cleaned_response = response.strip()
        # if cleaned_response.startswith("```sql")
        if cleaned_response.startswith("```sql") and cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[6:-3].strip()
        elif cleaned_response.startswith("```") and cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[3:-3].strip()
        
        if not cleaned_response or cleaned_response == "sql":
            logger.error(f"[generate_sql_query] Invalid or empty SQL response: {cleaned_response}")
            return "Error: Cannot generate SQL for this input"
            
        logger.info(f"[generate_sql_query] Cleaned SQL response: {cleaned_response}")
        return cleaned_response
        
    except Exception as e:
        logger.error(f"[generate_sql_query] Unexpected error: {str(e)}", exc_info=True)
        return f"Error: {str(e)}"

def analyze_db_schema(connection_id):
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"[analyze_db_schema] Starting for connection_id: {connection_id}")
        sqlalchemy_url = create_connection_url(connection_id)
        logger.info(f"[analyze_db_schema] Created connection URL")
        
        response = get_db_schema(sqlalchemy_url)
        
        return response
        
    except Exception as e:
        logger.error(f"[analyze_db_schema] Error getting schema: {str(e)}", exc_info=True)
        return f"Error getting schema: {str(e)}"

def create_connection_url(connection_id=None, db_name=None, db_host=None, db_port=None, db_user=None, db_password=None, db_type='postgres'):
    if connection_id:
        connection = Connection.objects.filter(id=connection_id).first()
        username = connection.username
        password = connection.password
        host = connection.host
        port = connection.port
        db_name = connection.db_name
        db_type = connection.db_type
        
        password = connection.get_password()

        if db_type == 'postgres':
            sqlalchemy_url = f"postgresql://{username}:{password}@{host}:{port}/{db_name}"
        elif db_type == 'mysql':
            sqlalchemy_url = f"mysql+pymysql://{username}:{password}@{host}:{port}/{db_name}"
        elif db_type == 'mssql':
            sqlalchemy_url = f"mssql+pyodbc://{username}:{password}@{host}:{port}/{db_name}?driver=ODBC+Driver+17+for+SQL+Server"
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
            
        return sqlalchemy_url
    
    if not connection_id:
        if db_type == 'postgres':
            sqlalchemy_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        elif db_type == 'mysql':
            sqlalchemy_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        elif db_type == 'mssql':
            sqlalchemy_url = f"mssql+pyodbc://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?driver=ODBC+Driver+17+for+SQL+Server"
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
            
        return sqlalchemy_url

# import logging
# from django.conf import settings
# from apps.home.models import Connection

# logger = logging.getLogger(__name__)

# def create_connection_url(connection_id=None, db_name=None, db_host=None, db_port=None, db_user=None, db_password=None, db_type='postgres'):
#     if connection_id:
#         try:
#             connection = Connection.objects.filter(id=connection_id).first()
#             if not connection:
#                 logger.error(f"No connection found for ID: {connection_id}")
#                 raise ValueError(f"No connection found for ID: {connection_id}")

#             username = connection.username
#             host = connection.host
#             port = connection.port
#             db_name = connection.db_name
#             db_type = connection.db_type

#             try:
#                 password = connection.get_password()
#                 logger.info(f"Successfully retrieved password for connection {connection_id}")
#             except Exception as e:
#                 logger.error(f"Failed to decrypt password for connection {connection_id}: {str(e)}")
#                 raise

#             if db_type == 'postgres':
#                 sqlalchemy_url = f"postgresql://{username}:{password}@{host}:{port}/{db_name}"
#             elif db_type == 'mysql':
#                 sqlalchemy_url = f"mysql+pymysql://{username}:{password}@{host}:{port}/{db_name}"
#             elif db_type == 'mssql':
#                 sqlalchemy_url = f"mssql+pyodbc://{username}:{password}@{host}:{port}/{db_name}?driver=ODBC+Driver+17+for+SQL+Server"
#             else:
#                 logger.error(f"Unsupported database type: {db_type}")
#                 raise ValueError(f"Unsupported database type: {db_type}")

#             logger.info(f"Generated SQLAlchemy URL for connection {connection_id}")
#             return sqlalchemy_url

#         except Exception as e:
#             logger.error(f"Error creating connection URL for connection {connection_id}: {str(e)}")
#             raise

#     if not connection_id:
#         if not all([db_name, db_host, db_port, db_user, db_password]):
#             logger.error("Missing required database connection parameters")
#             raise ValueError("All database connection parameters (db_name, db_host, db_port, db_user, db_password) are required")

#         if db_type == 'postgres':
#             sqlalchemy_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
#         elif db_type == 'mysql':
#             sqlalchemy_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
#         elif db_type == 'mssql':
#             sqlalchemy_url = f"mssql+pyodbc://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?driver=ODBC+Driver+17+for+SQL+Server"
#         else:
#             logger.error(f"Unsupported database type: {db_type}")
#             raise ValueError(f"Unsupported database type: {db_type}")

#         logger.info("Generated SQLAlchemy URL from provided parameters")
#         return sqlalchemy_url


def trigger_sql_query(sql, connection_id):
    #sql, connection_id = request.GET.get('sql'), request.GET.get('connection_id')
    connection_url = create_connection_url(connection_id)
    print(connection_url)
    result = run_sql_query(sql, connection_url)
    print(result)
    return JsonResponse(result, safe=False)

def detect_visualization_type(df):
    num_columns = len(df.columns)

    if num_columns == 1:
        return "pie"
    elif num_columns == 2:
        if df.dtypes[1] == "int64" or df.dtypes[1] == "float64":
            return "bar"
        elif df.dtypes[1] == "datetime64[ns]":
            return "line"
        else:
            return "scatter"
    elif num_columns >= 3 and (df.dtypes[2] == "int64" or df.dtypes[2] == "float64"):
        return "heatmap"
    else:
        return "bar"

def create_visualization(df, visualization_type, title):
    if visualization_type == "bar":
        fig = px.bar(df, x=df.columns[0], y=df.columns[1], title=title)
    elif visualization_type == "pie":
        fig = px.pie(df, names=df.columns[0], title=title)
    elif visualization_type == "line":
        fig = px.line(df, x=df.columns[0], y=df.columns[1], title=title)
    elif visualization_type == "scatter":
        fig = px.scatter(df, x=df.columns[0], y=df.columns[1], title=title)
    elif visualization_type == "histogram":
        fig = px.histogram(df, x=df.columns[0], nbins=20, title=title)
    elif visualization_type == "box":
        fig = px.box(df, x=df.columns[0], y=df.columns[1], title=title)
    elif visualization_type == "heatmap":
        fig = px.density_heatmap(df, x=df.columns[0], y=df.columns[1], z=df.columns[2], title=title)
    elif visualization_type == "table":
        fig = go.Figure(data=[go.Table(header=dict(values=df.columns), cells=dict(values=[df[col] for col in df.columns]))])
        fig.update_layout(title=title)
    else:
        raise ValueError(f"Unsupported visualization type: {visualization_type}")

    return fig.to_html(full_html=False)
