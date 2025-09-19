from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
import json
import os
import traceback
from retell import Retell

@csrf_protect
@require_http_methods(["POST"])
def start_call(request):
    try:
        data = json.loads(request.body)
        prompt = data.get('prompt')

        if not prompt:
            return JsonResponse({'error': 'Missing prompt'}, status=400)

        # Initialize Retell client with your API key
        api_key = os.getenv('RETELL_API_KEY')
        print(f"API Key present: {bool(api_key)}")
        retell = Retell(api_key=api_key)
        print(f"Retell client: {retell}")

        # Create a Retell LLM with default prompt if none provided
        default_prompt = """You are a helpful assistant that answers questions about sample data tables. 
        Here are some example tables you can talk about:
        - customers (id, name, email, country)
        - orders (id, customer_id, order_date, total_amount)
        - products (id, name, price, category)
        
        Please be succinct in your responses and focus on helping users understand their data."""
        
        llm = retell.llm.create(
            type="retell-llm",
            model="claude-3.5-sonnet",
            general_prompt=prompt or default_prompt,
            temperature=0.7
        )
        print(f"Created LLM: {llm}")

        # Create agent using the LLM ID
        agent = retell.agent.create(
            response_engine={
                "llm_id": llm.llm_id,
                "type": "retell-llm",
            },
            agent_name="Data Assistant",
            voice_id="11labs-Myra",
        )
        print(f"Created agent: {agent}")

        return JsonResponse({
            'success': True,
            'agent_id': agent['agent_id'],
            'llm_id': agent['response_engine']['llm_id']
        })

    except Exception as e:
        error_msg = str(e)
        print(f"Error in start_call: {error_msg}")
        print(f"Traceback: {traceback.format_exc()}")
        
        if 'rate limit exceeded' in error_msg.lower():
            return JsonResponse({
                'error': 'Rate limit exceeded. Please try again in about an hour.'
            }, status=429)
        
        return JsonResponse({
            'error': error_msg
        }, status=500)
