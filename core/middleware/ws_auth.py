from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken

User =get_user_model()

@database_sync_to_async
def get_user(token):
    try:
        access =AccessToken(token=token)
        return User.objects.get(id=access['user_id'])
    except:
        return None

class JWTAuthMiddleware:
    def __init__(self,app):
        self.app = app
    async def __call__(self,scope,receive,send, *args, **kwds):
        query_str = parse_qs(scope['query_string'].decode())
        token = query_str.get('token')

        if token:
            user = await get_user(token[0])
            scope['user'] = user
        else:
            scope['user'] =None
        return await self.app(scope,receive,send)