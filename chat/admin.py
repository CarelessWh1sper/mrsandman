from django.contrib import admin

from .models import Message, Room, Topic


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'topic', 'host', 'created')
    list_filter = ('topic',)
    search_fields = ('name', 'description')


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    search_fields = ('name',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'created', 'body')
    list_filter = ('room',)
