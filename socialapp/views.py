from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, views, login
from socialapp.models import SocialUser, Chats, ChatsUsers, ChatMessages, Posts, Likes
from socialapp.forms import RegistrationFormUser, RegistrationFormSocialUser, LoginForm
from django.db.models import Q
from django.core.mail import send_mail
from datetime import datetime, timedelta
from crossbarhttp import *

def index(request):
    isAuth = False
    username = ""
    post_dict = {}
    if request.user.is_authenticated():
        isAuth = True
        username = request.user.username
        all_posts_and_comments = Posts.objects.all().filter(Q(user=request.user) | Q(user__in=SocialUser.objects.get(user=request.user).friends.all())).order_by("date_created")
        for post in all_posts_and_comments:
            post_likes = Likes.objects.filter(post=post)
            if len(Likes.objects.filter(post=post)) > 0:
                liked_alredy = True
            else:
                liked_alredy = False
            post_image = ""
            if post.image:
                post_image = post.image.url
            if post.parent is None:
                post_dict["post_"+str(post.id)]={"postId":post.id,"post_creator_id":post.user.id, "post_creator_username":post.user.username, "post_text":post.text,"post_image":post_image,"post_likes":len(post_likes), "liked_alredy":liked_alredy, "post_comments":[], "post_date_created": post.date_created}
            else:
                post_dict["post_"+post.parent.id]["comments"].append({"commentId":post.id,"comment_creator_id":post.user.id, "comment_creator_username":post.user.username, "comment_text":post.text,"comment_image":post_image,"comment_likes":len(post_likes), "liked_alredy":liked_alredy})
    #print sorted(post_dict.values(), key=lambda k: k['post_date_created'], reverse=True)
    return render(request, 'index.html', {'user':{'is_authenticated':isAuth, 'username':username, "user_id":request.user.id}, "posts":sorted(post_dict.values(), key=lambda k: k['post_date_created'], reverse=True)})

def remove_post(request):
    post_id = request.POST["post_id"]
    post = Posts.objects.get(id=post_id)
    post.delete()
    return JsonResponse({"operation":"success", "post_id":post_id})

def register(request):
    if request.method == "POST":
        formUser = RegistrationFormUser(data = request.POST.copy())
        formSocialUser = RegistrationFormSocialUser(data = request.POST.copy())
        if formUser.is_valid() and formSocialUser.is_valid():
            registrationUser= formUser.save()
            registrationUser.set_password(registrationUser.password)
            registrationUser.save()
            registrationSocialUser= formSocialUser.save(commit=False)
            registrationSocialUser.user = registrationUser
            registrationSocialUser.save()
            send_mail("Success registration on Django Social App", "Bravo, login data: username: "+registrationUser.username+", password: "+ registrationUser.password, None, [registrationUser.email], fail_silently=False)
            return render(request, 'index.html')
        else:
            formUser = RegistrationFormUser()
            formSocialUser = RegistrationFormSocialUser()
            return render(request, 'registration/registration_form.html', {'formUser':formUser, 'formSocialUser':formSocialUser})
    else:
        formUser = RegistrationFormUser()
        formSocialUser = RegistrationFormSocialUser()
        return render(request, 'registration/registration_form.html', {'formUser':formUser, 'formSocialUser':formSocialUser})

def create_new_chat(request):
    chat_creator = SocialUser.objects.get(id= request.POST['creator_id'])
    chat_title = request.POST['title']
    chat_users = request.POST['users_id']
    date_created = datetime.datetime.now()
    last_modified = date_created
    chat = Chats(creator=chat_creator, date_created = date_created, title = chat_title, last_modified = last_modified)
    chat.save()
    client = Client("http://127.0.0.1:8080/publish")
    for chat_user in chat_users:
        social_user = SocialUser.objects.get(id=chat_user)
        chats_users = ChatsUsers(chat = chat, user = social_user)
        chats_users.save()
        result = client.publish(topic="SocialUserId."+social_user.id, data={"event":"new_chat","chat_data":{"chat_creator_id":chat_creator.id, "chat_title": chat_title, "last_modified": last_modified}})

def send_message(request):
    chat_id = request.POST['chat_id']
    chat = Chats.objects.get(id=chat_id)
    message = request.POST['message']
    sender = SocialUser.objects.get(id=request.POST['sender_id'])
    chats_users = ChatsUsers.objects.filter(chat = chat)
    if chats_users.filter(user=sender) is not None:
        chats_users_model = ChatsUsers(chat=chat, user= sender)
        chats_users_model.save()
    chats_users = chats_users.exclude(user= sender)
    client = Client("http://127.0.0.1:8080/publish")
    for chat_user in chats_users:
        result = client.publish(topic="SocialUserId."+chat_user.user.id, data={"event":"new_msg","msg_data":{"msg_sender_id":sender.id, "chat_id": chat_user.chat.id, "msg_content": message}})
    chat_message = ChatMessages(text = message, date_pub = datetime.now(), chat = chat, user = sender)
    chat_message.save()

def publish_post(request):
    post = Posts(user=request.user, date_created = datetime.now(), text=request.POST["post_text"])
    if len(request.FILES) > 0:
        post.image = request.FILES["input-file-preview"]
    post.save()
    return HttpResponseRedirect("/")

def logout_user(request):
    if request.user.is_authenticated():
        views.logout(request ,template_name="index.html")
    isAuth = False
    username = ""
    print isAuth
    return render(request, 'index.html', {'user':{'is_authenticated':isAuth, 'username':username}})

def login_user(request):
    if request.method == "POST":
        formLogin = LoginForm(data=request.POST)
        print formLogin.is_valid()
        if formLogin.is_valid() :
            user = authenticate(username=request.POST['username'], password=request.POST['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    # Redirect to a success page.
                    return render(request, 'index.html')
                else:
                    # Return a 'disabled account' error message
                    print "disabled account"
            else:
                # Return an 'invalid login' error message.
                print "invalid login"
        else:
            formLogin = LoginForm()
            return render(request, 'registration/login.html', {'formLogin':formLogin})
    else:
        formLogin = LoginForm()
        return render(request, 'registration/login.html', {'formLogin':formLogin})
