from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Message, Room, Topic

User = get_user_model()


class StyledMixin:
    """Gives every field the same input style as the rest of the site."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'Boxinput'


class LoginForm(StyledMixin, AuthenticationForm):
    pass


class SignUpForm(StyledMixin, UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ('username',)


class UserForm(StyledMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']


class RoomForm(StyledMixin, forms.ModelForm):
    topic = forms.CharField(max_length=200, help_text='Pick one from the list or type a new one.')

    class Meta:
        model = Room
        fields = ['name', 'description']
        widgets = {'description': forms.Textarea(attrs={'rows': 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_fields(['name', 'topic', 'description'])
        self.fields['topic'].widget.attrs['list'] = 'topic-list'
        self.fields['description'].required = False
        if self.instance.pk and self.instance.topic:
            self.initial['topic'] = self.instance.topic.name

    def clean_topic(self):
        return ' '.join(self.cleaned_data['topic'].split())

    def get_topic(self):
        name = self.cleaned_data['topic']
        return Topic.objects.filter(name__iexact=name).first() or Topic.objects.create(name=name)


class MessageForm(StyledMixin, forms.ModelForm):
    class Meta:
        model = Message
        fields = ['body']
        labels = {'body': 'Message'}
        widgets = {'body': forms.Textarea(attrs={'rows': 4, 'maxlength': 500})}
