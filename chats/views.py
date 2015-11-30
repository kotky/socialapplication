from django.shortcuts import render
from django.contrib.auth.models import User
from socialapp.models import ChatMessages,Chats
from django.db.models import Q

# Create your views here.
def index(request):
    isAuth = False
    username = ""
    chat_array = []
    if request.user.is_authenticated():
        isAuth = True
        username = request.user.username
        all_chats = Chats.objects.filter(creator=request.user) | Chats.objects.filter(users__in = [request.user])
        print all_chats
        for chat in all_chats:
            all_messages = ChatMessages.objects.filter(chat=chat).order_by("date_pub")
    return render(request, 'index.html', {'user':{'is_authenticated':isAuth, 'username':username, "user_id":request.user.id}, 'chat':{}})
