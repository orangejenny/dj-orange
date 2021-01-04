class NoCacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['Cache-Control'] = "private, no-cache, no-store, must-revalidate, proxy-revalidate"
        response['Expires'] = "Sun, 01 Dec 2002 16:00:00 GMT"
        response['Pragma'] = "no-cache"
        return response
