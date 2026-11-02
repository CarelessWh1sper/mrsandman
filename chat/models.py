from django.conf import settings
from django.db import models


class Topic(models.Model):
    name = models.CharField(max_length=200, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Room(models.Model):
    host = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                             null=True, related_name='hosted_rooms')
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='rooms')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chat_rooms',
                                          blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.name


class Message(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='chat_messages')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
    body = models.TextField(max_length=500)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created']

    def __str__(self):
        return self.body[:50]

    @property
    def edited(self):
        return (self.updated - self.created).total_seconds() > 2
