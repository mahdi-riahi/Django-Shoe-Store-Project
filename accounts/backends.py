from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class EmailOrPhoneBackend:
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        try:
            user = User.objects.get(Q(email=username)|Q(phone_number=username))
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
