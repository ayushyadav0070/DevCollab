from channels.generic.websocket import AsyncJsonWebsocketConsumer
import json
from channels.db import database_sync_to_async
from workspaces.models import Membership

@database_sync_to_async
def is_memeber(user,workspace_id):
    return Membership.objects.filter(
        user =user,
        workspace_id=workspace_id
    ).exists()
class TaskConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user  = self.scope['user']
        if not await(self.user,self.workspace_id):
            await self.close(code=4003)
            return
        self.workspace_id  =self.scope['url_route']['kwargs']['workspace_id']
        self.group_name = f"workspace_{self.workspace_id}"

        await self.channel_layer.group_add(
            self.group_name,self.channel_name
        )
        await self.accept()
    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.group_name,self.channel_name
        ) 
    async def task_update(self,event):
        await self.send(text_data=json.dumps(event["data"]))
         
class PresenceConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.workspace_id = self.scope['url_route']['kwargs']['workspace_id']
        self.group_name  = f"presence_{self.workspace_id}"

        await self.channel_layer.group_add(self.group_name,self.channel_name)
        await self.accept()
        await self.channel_layer.group_send(
            self.group_name,{
                "type":"presence_update",
                "message": "user joined"}
        )
    async def presence_update(self,event):
        await self.send(text_data=json.dumps(event))
    async def disconnect(self, code):
        await self.channel_layer.group_send(
            self.group_name,{
                "type":"presence_update",
                "message":"user left"
            }
        )