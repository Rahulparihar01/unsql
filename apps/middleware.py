import logging
from django.contrib.sessions.middleware import SessionMiddleware

logger = logging.getLogger('apps.middleware')

class ConditionalSessionMiddleware(SessionMiddleware):
    def process_request(self, request):
        logger.debug(f"Processing request for path: {request.path}")
        if request.path == '/':
            logger.debug("Skipping session creation for homepage")
            return None
        logger.debug("Applying session middleware")
        return super().process_request(request)

    def process_response(self, request, response):
        if request.path == '/':
            logger.debug("Skipping session save for homepage")
            return response
        return super().process_response(request, response)