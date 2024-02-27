import json
from channels.consumer import AsyncConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Thread,ChatMessage,Group,GroupMessage
# from chat.models import Thread, ChatMessage
from asgiref.sync import sync_to_async


User = get_user_model()


class ChatConsumer(AsyncConsumer):
    async def websocket_connect(self, event):

        await self.send({
            'type': 'websocket.accept'
        })

        user = self.scope['user']
        threads = await self.get_user_threads(user)
        gropus = await self.get_user_groups(user)

        for thread in threads:
            chat_room = f'chatroom_{thread.unique_id}'
            await self.channel_layer.group_add(
                chat_room,
                self.channel_name
            )

        for group in gropus:
            chat_room = f'chatroom_{group.unique_id}'
            await self.channel_layer.group_add(
                chat_room,
                self.channel_name
            )

    async def websocket_receive(self, event):
        # print('receive', event)
        received_data = json.loads(event['text'])
        print(received_data)
        msg = received_data.get('message')
        sent_by_id = received_data.get('sent_by')
        # thread_or_group_id = received_data.get('thread_or_group_id')
        unique_id = received_data.get('unique_id')

        if not msg:
            print('Error:: empty message')
            return False
        
        if not unique_id:
            print('Error: unique_id is missing')
            return
        
        chat_room = f'chatroom_{unique_id}'
        self.chat_room = chat_room


        sent_by_user = await self.get_user_object(sent_by_id)
        sent_by_username = sent_by_user.username
        print(f"{sent_by_username}")
        thread_or_group_obj = await self.get_thread_or_group(unique_id)

        if not sent_by_user:
            print('Error:: sent by user is incorrect')
        if not thread_or_group_obj:
            print('Error:: Thread or Group id is incorrect')

        chat_message = await self.create_chat_or_group_message(thread_or_group_obj, sent_by_user, msg)

        formatted_timestamp = chat_message.timestamp.strftime("%d %b, %H:%M")
        print(formatted_timestamp)

        
        self_user = self.scope['user']
        response = {
            'message': msg,
            'sent_by': self_user.id,
            # 'thread_or_group_id': thread_or_group_id,
            'unique_id': unique_id,
            'sent_by_username':sent_by_username,
            'timestamp': formatted_timestamp,
        }


        await self.channel_layer.group_send(
            self.chat_room,
            {
                'type': 'chat_message',
                'text': json.dumps(response)
            }
        )



    async def websocket_disconnect(self, event):
        print('disconnect', event)


    async def chat_message(self, event):
        # print('chat_message', event)
        await self.send({
            'type': 'websocket.send',
            'text': event['text']
        })



    @database_sync_to_async
    def get_user_object(self, user_id):
        return User.objects.filter(id=user_id).first()

    @database_sync_to_async
    def get_thread_or_group(self, unique_id):
        thread = Thread.objects.filter(unique_id=unique_id).first()
        if thread:
            return thread
        else:
            return Group.objects.filter(unique_id=unique_id).first()


    @database_sync_to_async
    def create_chat_or_group_message(self, thread_or_group_obj, user, msg):
        chat_message = None
        if isinstance(thread_or_group_obj, Thread):
            chat_message = ChatMessage.objects.create(thread=thread_or_group_obj, user=user, message=msg)
        elif isinstance(thread_or_group_obj, Group):
            chat_message = GroupMessage.objects.create(group=thread_or_group_obj, user=user, message=msg)
        return chat_message


    @database_sync_to_async
    def get_user_threads(self, user):
        return list(Thread.objects.by_user(user=user))
    
    @database_sync_to_async
    def get_user_groups(self, user):
        return list(Group.objects.filter(members=user))

    
    
