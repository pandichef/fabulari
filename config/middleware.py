from django.utils.translation import activate
from accounts.models import CustomUser as UserProfile


class UserLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get the current user (assuming the user is authenticated)
        if request.user.is_authenticated:
            print("11111111111")
            print(request.user.native_language)
            activate(request.user.native_language)
            # request.LANGUAGE_CODE = request.user.native_language
        else:
            print("asdfsadf")
            # Fallback to default language
            activate("en")

        response = self.get_response(request)
        # translation.deactivate()
        return response
