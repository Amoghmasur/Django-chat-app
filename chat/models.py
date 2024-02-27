from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Q
import uuid


User = get_user_model()

# Create your models here.

class ThreadManager(models.Manager):
    def by_user(self, **kwargs):
        user = kwargs.get('user')
        lookup = Q(first_person=user) | Q(second_person=user)
        qs = self.get_queryset().filter(lookup).distinct()
        return qs


class Thread(models.Model):
    first_person = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='thread_first_person')
    second_person = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                                     related_name='thread_second_person')
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    unique_id = models.UUIDField(default=uuid.uuid4, unique=True,blank=True, null=True)


    objects = ThreadManager()
    class Meta:
        unique_together = ['first_person', 'second_person']



class ChatMessage(models.Model):
    thread = models.ForeignKey(Thread, null=True, blank=True, on_delete=models.CASCADE, related_name='chatmessage_thread')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    delivery_status = models.BooleanField(default=False)    

    
    def __str__(self):
        return f"{self.user} - {self.message[:50]}"
    






class Group(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User)
    created_at = models.DateTimeField(auto_now_add=True)

    unique_id = models.UUIDField(default=uuid.uuid4, unique=True,blank=True, null=True)


    def __str__(self):
        return self.name

class GroupMessage(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='groupmessage_group')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.message[:50]}"
