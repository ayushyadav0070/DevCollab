from django.urls import  re_path
from .consumers import TaskConsumer, PresenceConsumer
 
websocket_urlpatterns = [
    re_path(r'ws/tasks/(?P<workspace_id>\d+)/$', TaskConsumer.as_asgi()),
    re_path(r'ws/presence/(?P<workspace_id>\d+)/$', PresenceConsumer.as_asgi()),
]