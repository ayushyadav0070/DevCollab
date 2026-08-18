from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

class EmailorUsernamelogin(ModelBackend):
    def authenticate(self, request, username = None, password = None, **kwargs):
        
        UserModel =get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if not username:
            return None
        try:
            user = UserModel.objects.get(
                Q(username__iexact=username) |Q(email__iexact=username) 
            )
        
        except UserModel.DoesNotExist:
            return None
        except UserModel.MultipleObjectsReturned:
            return None
        if user.check_password(password) and self.user_can_authenticate(user=user):
            return user

        return None