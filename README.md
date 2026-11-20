# Mr. Sandman

A small website for people who are awake late at night.

- A **landing page** ("What's keeping you up tonight?")
- An **About page** with a music player: a moon you tap to play, lyrics that follow the song word by word, a progress bar and 10-second skip buttons
- A **live chat** where signed-in people open rooms about what is keeping them up, and everyone else can watch
- **Tonight and Archive**: tonight's rooms and messages are shown on one page, and earlier nights are kept in an archive
- Works on desktop, tablet and phone

Built with Django, Channels (live messages over WebSockets) and plain HTML, CSS and JavaScript.

---

## Contents

1. [Features](#features)
2. [Requirements](#requirements)
3. [Setup](#setup)
4. [Configuration](#configuration)
5. [Project structure](#project-structure)
6. [Pages and URLs](#pages-and-urls)
7. [How "tonight" works](#how-tonight-works)
8. [How the live chat works](#how-the-live-chat-works)
9. [Troubleshooting](#troubleshooting)
10. [Before you put it online](#before-you-put-it-online)

---

## Features

**Chat**

- Rooms with a name, a description, a topic and a host
- Messages appear instantly for everyone in the room, with no page refresh
- Anyone can watch a room; only signed-in users can post (up to 500 characters)
- Edit or delete your own messages; edit or delete the rooms you host
- Participants list that updates live as people post
- Search rooms by name, description or topic
- Topics page, recent activity, and a profile page for every user
- Sign up, sign in and sign out with usernames

**Tonight and Archive**

- *Tonight* shows only the rooms and messages made since the latest night began
- *Archive* shows rooms from earlier nights, grouped by night

**Player (About page)**

- Play and pause by tapping the moon, or with the space bar
- Lyrics follow the song; previous and next lines are shown faintly
- Progress bar you can tap, 10-second back and forward buttons, and left/right arrow keys

**Design**

- One dark night-sky look across every page
- Responsive: the navigation becomes a menu button on small screens, and the layouts adapt to phones and tablets

---

## Requirements

- Python 3.12
- The packages in `requirements.txt` (Django, Channels, Daphne)

No other database is needed: the project uses SQLite, which comes with Python.

---

## Setup

These commands are for Windows PowerShell. On macOS or Linux, use `python3` instead of `python`, and `source venv/bin/activate` to activate the virtual environment.

**1. Open the project folder** (the one that contains `manage.py`):

```powershell
cd "C:\Users\Administrator\Desktop\Final 1.0"
```

**2. Create and activate a virtual environment** (recommended, so the packages stay inside this project):

```powershell
python -m venv venv
venv\Scripts\activate
```

If PowerShell refuses to run the activation script, run this once and try again:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

**3. Install the packages:**

```powershell
pip install -r requirements.txt
```

**4. Create the database tables:**

```powershell
python manage.py migrate
```

**5. Create an admin account** (optional, but useful for managing rooms and topics):

```powershell
python manage.py createsuperuser
```

**6. Start the server:**

```powershell
python manage.py runserver
```

The first lines of the output should say `Starting ASGI/Daphne ... development server`. If they don't, see [Troubleshooting](#troubleshooting).

**7. Open the site:** <http://127.0.0.1:8000/home/>

To try the chat with two people, open the site in a normal browser window and a private window, sign up with a different username in each, and join the same room.

> Use `127.0.0.1` or `localhost` in the address bar. Live chat messages are refused on other addresses (such as your computer's network IP) until you add them to `ALLOWED_HOSTS`.

---

## Configuration

Everything is in `base/settings.py`.

**Apps.** `daphne` must be the **first** entry:

```python
INSTALLED_APPS = [
    'daphne',                      # must come first
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',
    'chat',
]
```

**Live messages and sign-in:**

```python
ASGI_APPLICATION = 'base.asgi.application'

CHANNEL_LAYERS = {
    'default': {'BACKEND': 'channels.layers.InMemoryChannelLayer'},
}

LOGIN_URL = 'chat:login'
LOGIN_REDIRECT_URL = 'chat:home'
LOGOUT_REDIRECT_URL = 'home'
```

**Time zone and the start of a night.** Set `TIME_ZONE` to yours, otherwise a night is counted in UTC:

```python
TIME_ZONE = 'Europe/Berlin'        # your own time zone

CHAT_NIGHT_START_HOUR = 18         # optional, 0-23, default is 18 (6 PM)
```

**URLs.** `base/urls.py` includes the chat app:

```python
path('', include('chat.urls')),
```

---

## Project structure

```
Final 1.0/
├── manage.py
├── requirements.txt
├── README.md
│
├── base/                      Project settings
│   ├── settings.py
│   ├── urls.py                Landing, About and old sign-in page + chat URLs
│   └── asgi.py                Routes normal pages and WebSocket (live chat) traffic
│
├── chat/                      The chat app
│   ├── models.py              Topic, Room, Message
│   ├── views.py               Tonight, archive, rooms, messages, profiles, sign up
│   ├── forms.py               Styled login, sign-up, room, message and profile forms
│   ├── consumers.py           Live chat (WebSocket) logic
│   ├── routing.py             WebSocket URL: /ws/chat/<room id>/
│   ├── nights.py              Decides what counts as "tonight"
│   ├── urls.py
│   ├── admin.py
│   ├── migrations/
│   └── templates/chat/        base.html, home.html (Tonight), archive.html,
│                              room.html, topics.html, activity.html, profile.html,
│                              login.html, signup.html, and the forms
│
├── templates/                 index.html, about.html, signIn.html
│
├── static/
│   ├── css/
│   │   ├── style.css          Main styles and the night-sky background
│   │   ├── chat.css           Chat pages
│   │   └── responsive.css     Phone and tablet layouts, collapsing menu
│   └── SYML-Mr.-Sandman-320.mp3   The song played on the About page (plus your fonts)
│
└── db.sqlite3                 Created by "migrate"
```

---

## Pages and URLs

| Address | What it shows |
|---|---|
| `/home/` | Landing page |
| `/about/` | Music player with lyrics |
| `/signIn/` | Old sign-in mockup (the real sign-in is `/accounts/login/`) |
| `/chat/` | **Tonight**: rooms and messages from the current night |
| `/chat/archive/` | **Archive**: rooms from earlier nights, grouped by night |
| `/chat/room/<id>/` | A live room |
| `/chat/create-room/` | Create a room (signed in) |
| `/chat/room-update/<id>/` | Edit a room (host only) |
| `/chat/delete/<id>/` | Delete a room (host only) |
| `/chat/edit-message/<id>/` | Edit a message (author only) |
| `/chat/delete-message/<id>/` | Delete a message (author only) |
| `/chat/topics/` | All topics, with room counts for tonight and earlier |
| `/chat/activity/` | Tonight's messages (`?when=past` for earlier nights) |
| `/chat/profile/<id>/` | A user's profile and hosted rooms |
| `/chat/edit-profile/` | Edit your own username and email |
| `/accounts/login/` | Sign in |
| `/accounts/signup/` | Create an account |
| `/admin/` | Django admin |

---

## How "tonight" works

A night starts at `CHAT_NIGHT_START_HOUR` (6 PM by default) in your `TIME_ZONE` and lasts until the next one starts.

- Everything made since the **latest** 6 PM is *tonight*.
- Everything made before that is in the *archive*.

So at 10 AM, "Tonight" still shows last night, and at 6 PM it starts fresh and the previous night moves to the archive.

The rule is a room's or message's **creation time**. A room from an earlier night stays in the archive even if people are still talking in it, and those new messages appear in tonight's activity.

The logic is in `chat/nights.py`.

---

## How the live chat works

- Opening a room connects the page to `ws://<host>/ws/chat/<room id>/`.
- Anyone can connect and watch. Only signed-in users can send; messages from others are ignored.
- A sent message is saved to the database, the sender is added to the room's participants, and the message is broadcast to everyone in the room.
- If the connection drops, the page reconnects by itself (the status under the room name says **Live** or **Reconnecting…**).
- Edits and deletes use normal pages and are not pushed live to other people.

---

## Troubleshooting

**The room says "Reconnecting…" and the message box is disabled**
The server isn't running in live (ASGI) mode. Check that:

1. `'daphne'` is the first item in `INSTALLED_APPS`.
2. `ASGI_APPLICATION = 'base.asgi.application'` is in `settings.py`.
3. `base/asgi.py` contains `ProtocolTypeRouter` and `chat.routing`.
4. The server output starts with `Starting ASGI/Daphne`.
5. You opened the site on `127.0.0.1` or `localhost`.

**`daphne.E001: Daphne must be listed before django.contrib.staticfiles`**
Move `'daphne'` to the top of `INSTALLED_APPS`.

**`NoReverseMatch: Reverse for 'rooms' not found`**
`LOGIN_REDIRECT_URL` still uses an old page name. Set it to `'chat:home'`.

**`no such table: chat_topic`**
The tables haven't been created. Run `python manage.py makemigrations chat`, then `python manage.py migrate`.

**`makemigrations` asks "Was message.content renamed to message.body?"**
Press Ctrl+C. Run `python manage.py migrate chat zero`, delete `chat/migrations/0001_initial.py` (keep `__init__.py`), then run `makemigrations chat` and `migrate` again.

**The 10-second buttons or the progress bar do nothing**
The development server can't send the song in pieces, so the browser won't jump around in it. The About page works around this by loading the song into memory on the first jump, so use the current `about.html`.

**"Tonight" shows the wrong rooms**
`TIME_ZONE` is probably still `'UTC'`. Set it to your own time zone.

**The page looks unstyled or old after an update**
Restart the server and hold Ctrl while pressing F5 to reload the CSS.

---

## Before you put it online

This setup is for development. For a public site:

- Set `DEBUG = False` and fill in `ALLOWED_HOSTS` with your domain
- Use a new, secret `SECRET_KEY` and keep it out of version control
- Replace the in-memory channel layer with Redis (`channels-redis`), because the in-memory one only works inside a single process:

  ```python
  CHANNEL_LAYERS = {
      'default': {
          'BACKEND': 'channels_redis.core.RedisChannelLayer',
          'CONFIG': {'hosts': [('127.0.0.1', 6379)]},
      },
  }
  ```

- Run the site with an ASGI server such as Daphne or Uvicorn, and serve static files with a web server or WhiteNoise (run `python manage.py collectstatic`)
- Do not publish `db.sqlite3`
- The song and its lyrics belong to their rights holders. Make sure you have permission to use them before the site is public.
