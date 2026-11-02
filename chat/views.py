from itertools import groupby

from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import MessageForm, RoomForm, SignUpForm, UserForm
from .models import Message, Room, Topic
from .nights import night_of, tonight_start

User = get_user_model()

HISTORY_LIMIT = 100
ARCHIVE_LIMIT = 200


def _rooms_with_counts(queryset):
    return (queryset.select_related('host', 'topic')
            .annotate(participant_count=Count('participants', distinct=True)))


def _match_rooms(q):
    return Q(topic__name__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q)


def _match_messages(q):
    return Q(room__topic__name__icontains=q) | Q(room__name__icontains=q)


def _topics(start, past=False):
    """Topics with the number of rooms made tonight (or on earlier nights)."""
    condition = Q(rooms__created__lt=start) if past else Q(rooms__created__gte=start)
    return (Topic.objects.annotate(room_count=Count('rooms', filter=condition))
            .filter(room_count__gt=0).order_by('-room_count', 'name'))



def home(request):
    """Tonight: rooms and messages made since tonight began."""
    start = tonight_start()
    q = request.GET.get('q', '').strip()
    rooms = _rooms_with_counts(
        Room.objects.filter(created__gte=start).filter(_match_rooms(q)))
    recent_messages = (Message.objects.filter(created__gte=start).filter(_match_messages(q))
                       .select_related('user', 'room').order_by('-created')[:6])
    return render(request, 'chat/home.html', {
        'q': q,
        'start': start,
        'rooms': rooms,
        'rooms_count': rooms.count(),
        'all_count': Room.objects.filter(created__gte=start).count(),
        'topics': _topics(start)[:6],
        'recent_messages': recent_messages,
        'panel_url': 'chat:home',
        'panel_title': 'Topics tonight',
    })


def archive(request):
    """Rooms and messages from past nights, grouped by night."""
    start = tonight_start()
    q = request.GET.get('q', '').strip()
    rooms = list(_rooms_with_counts(
        Room.objects.filter(created__lt=start).filter(_match_rooms(q))
    ).order_by('-created')[:ARCHIVE_LIMIT])
    nights = [{'date': night, 'rooms': list(group)}
              for night, group in groupby(rooms, key=lambda r: night_of(r.created))]
    past_messages = (Message.objects.filter(created__lt=start).filter(_match_messages(q))
                     .select_related('user', 'room').order_by('-created')[:8])
    return render(request, 'chat/archive.html', {
        'q': q,
        'nights': nights,
        'rooms_count': len(rooms),
        'all_count': Room.objects.filter(created__lt=start).count(),
        'topics': _topics(start, past=True)[:6],
        'past_messages': past_messages,
        'panel_url': 'chat:archive',
        'panel_title': 'Topics in the archive',
    })


def activity(request):
    start = tonight_start()
    past = request.GET.get('when') == 'past'
    messages = Message.objects.filter(created__lt=start) if past else \
        Message.objects.filter(created__gte=start)
    return render(request, 'chat/activity.html', {
        'recent_messages': messages.select_related('user', 'room').order_by('-created')[:50],
        'past': past,
    })


def topics(request):
    start = tonight_start()
    q = request.GET.get('q', '').strip()
    topic_list = (Topic.objects.filter(name__icontains=q).annotate(
        tonight_count=Count('rooms', filter=Q(rooms__created__gte=start)),
        earlier_count=Count('rooms', filter=Q(rooms__created__lt=start)),
    ).order_by('name'))
    return render(request, 'chat/topics.html', {'q': q, 'topics': topic_list})



def room_detail(request, pk):
    room = get_object_or_404(Room.objects.select_related('host', 'topic'), pk=pk)
    recent = room.messages.select_related('user').order_by('-created')[:HISTORY_LIMIT]
    return render(request, 'chat/room.html', {
        'room': room,
        'is_past': room.created < tonight_start(),
        'chat_messages': list(recent)[::-1],
        'participants': room.participants.order_by('username'),
    })


@login_required
def create_room(request):
    form = RoomForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        room = form.save(commit=False)
        room.host = request.user
        room.topic = form.get_topic()
        room.save()
        return redirect('chat:room', pk=room.pk)
    return render(request, 'chat/room_form.html', {
        'form': form, 'heading': 'Create a room', 'topics': Topic.objects.all(),
        'cancel_url': 'chat:home',
    })


@login_required
def update_room(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.user != room.host:
        raise PermissionDenied
    form = RoomForm(request.POST or None, instance=room)
    if request.method == 'POST' and form.is_valid():
        room = form.save(commit=False)
        room.topic = form.get_topic()
        room.save()
        return redirect('chat:room', pk=room.pk)
    return render(request, 'chat/room_form.html', {
        'form': form, 'heading': 'Edit room', 'topics': Topic.objects.all(),
        'cancel_url': 'chat:home',
    })


@login_required
def delete_room(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.user != room.host:
        raise PermissionDenied
    if request.method == 'POST':
        room.delete()
        return redirect('chat:home')
    return render(request, 'chat/delete.html', {
        'label': f'the room "{room.name}" and all its messages',
        'cancel_url': 'chat:room', 'cancel_pk': room.pk,
    })



@login_required
def edit_message(request, pk):
    message = get_object_or_404(Message, pk=pk)
    if request.user != message.user:
        raise PermissionDenied
    form = MessageForm(request.POST or None, instance=message)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('chat:room', pk=message.room_id)
    return render(request, 'chat/edit_message.html', {'form': form, 'room': message.room})


@login_required
def delete_message(request, pk):
    message = get_object_or_404(Message, pk=pk)
    if request.user != message.user:
        raise PermissionDenied
    if request.method == 'POST':
        room_id = message.room_id
        message.delete()
        return redirect('chat:room', pk=room_id)
    return render(request, 'chat/delete.html', {
        'label': 'this message',
        'cancel_url': 'chat:room', 'cancel_pk': message.room_id,
    })



def profile(request, pk):
    profile_user = get_object_or_404(User, pk=pk)
    start = tonight_start()
    rooms = _rooms_with_counts(Room.objects.filter(host=profile_user))
    recent_messages = (Message.objects.filter(user=profile_user)
                       .select_related('user', 'room').order_by('-created')[:6])
    return render(request, 'chat/profile.html', {
        'profile_user': profile_user,
        'rooms': rooms,
        'recent_messages': recent_messages,
        'topics': _topics(start)[:6],
        'all_count': Room.objects.filter(created__gte=start).count(),
        'panel_url': 'chat:home',
        'panel_title': 'Topics tonight',
        'no_active': True,
    })


def signup(request):
    if request.user.is_authenticated:
        return redirect('chat:home')
    form = SignUpForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('chat:home')
    return render(request, 'chat/signup.html', {'form': form})


@login_required
def edit_profile(request):
    form = UserForm(request.POST or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('chat:profile', pk=request.user.pk)
    return render(request, 'chat/edit_profile.html', {'form': form})
