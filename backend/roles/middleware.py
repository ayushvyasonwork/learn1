class LoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print(f"📩 Incoming {request.method} request to {request.path}")
        response = self.get_response(request)
        print(f"📤 Response status: {response.status_code}")
        return response
