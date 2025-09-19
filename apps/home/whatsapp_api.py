from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
# from heyoo import WhatsApp
from openai import OpenAI
import json
import os
from .models import Connection
from .util import analyze_db_schema

# class WhatsAppHandler:
#     def __init__(self):
#         self.messenger = WhatsApp(
#             os.getenv('WHATSAPP_TOKEN'),
#             phone_number_id=os.getenv('WHATSAPP_PHONE_NUMBER_ID')
#         )
#         self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
#         self._base_prompt = None
    
#     @property
#     def base_prompt(self):
#         return self._base_prompt
    
#     @base_prompt.setter
#     def base_prompt(self, value):
#         self._base_prompt = value
        
#     def get_ai_response(self, message):
#         if not self._base_prompt:
#             return "Error: Base prompt not configured"
            
#         messages = [
#             {"role": "system", "content": self._base_prompt},
#             {"role": "user", "content": message}
#         ]
        
#         response = self.openai_client.chat.completions.create(
#             model="gpt-4",
#             messages=messages,
#             temperature=0.7
#         )
        
#         return response.choices[0].message.content

#     def handle_message(self, from_number, message_body):
#         try:
#             # Get AI response
#             ai_response = self.get_ai_response(message_body)
            
#             # Send response via WhatsApp
#             # self.messenger.send_message(
#             #     ai_response,
#             #     from_number
#             # )
            
#             return "Message processed successfully"
#         except Exception as e:
#             print(f"Error processing message: {str(e)}")
#             return f"Error: {str(e)}"

# # Global handler instance
# whatsapp_handler = WhatsAppHandler()

@csrf_exempt
@require_http_methods(["POST"])
def webhook(request):
    # Handle WhatsApp verification
    # if 'hub.mode' in request.GET:
    #     return HttpResponse(request.GET.get('hub.challenge'))
    
    # Handle incoming messages
    data = json.loads(request.body)
    try:
        for entry in data['entry']:
            for change in entry['changes']:
                if change['value'].get('messages'):
                    for message in change['value']['messages']:
                        from_number = message['from']
                        message_body = message['text']['body']
                        # whatsapp_handler.handle_message(from_number, message_body)
        
        return HttpResponse("OK")
    except Exception as e:
        print(f"Error in webhook: {str(e)}")
        return HttpResponse(status=500)

@csrf_exempt
@require_http_methods(["POST"])
def configure(request):
    try:
        data = json.loads(request.body)
        connection_id = data.get('connection_id')
        
        if not connection_id:
            return JsonResponse({'error': 'Missing connection_id'}, status=400)
            
        # Get the database schema
        db_schema = analyze_db_schema(connection_id)
        if not db_schema:
            return JsonResponse({'error': 'Failed to get database schema'}, status=400)
            
        # Format the schema into a prompt
        base_prompt = "You are an AI assistant that helps users understand and query their database. "
        base_prompt += "Here is the database schema:\n\n"
        
        for table_name, table_info in db_schema.items():
            base_prompt += f"\nTable: {table_name}\n"
            base_prompt += "Columns:\n"
            for col_name, col_info in table_info['columns'].items():
                base_prompt += f"- {col_name} ({col_info['type']})\n"
            if table_info['relationships']:
                base_prompt += "Relationships:\n"
                for related_table, rel_info in table_info['relationships'].items():
                    base_prompt += f"- References {related_table} ({rel_info['local_column']} -> {rel_info['remote_column']})\n"
        
        # Update the handler's base prompt
        # whatsapp_handler.base_prompt = base_prompt
            
        return JsonResponse({
            'success': True,
            # 'message': 'WhatsApp configuration updated successfully'
            'message': 'Configuration updated successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)
