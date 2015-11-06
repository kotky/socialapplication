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
            if len(post_likes.filter(user=request.user)) > 0:
                liked_alredy = True
            else:
                liked_alredy = False
            post_image = ""
            if post.image:
                post_image = post.image.url
            if post.parent is None:
                post_dict["post_"+str(post.id)]={"postId":post.id,"post_creator_id":post.user.id, "post_creator_username":post.user.username, "post_text":post.text,"post_image":post_image,"likes_count":len(post_likes), "liked_alredy":liked_alredy, "post_comments":[], "post_date_created": post.date_created}
            else:
                post_dict["post_"+post.parent.id]["comments"].append({"commentId":post.id,"comment_creator_id":post.user.id, "comment_creator_username":post.user.username, "comment_text":post.text,"comment_image":post_image,"likes_count":len(post_likes), "liked_alredy":liked_alredy})
    #print sorted(post_dict.values(), key=lambda k: k['post_date_created'], reverse=True)
    return render(request, 'index.html', {'user':{'is_authenticated':isAuth, 'username':username, "user_id":request.user.id}, "posts":sorted(post_dict.values(), key=lambda k: k['post_date_created'], reverse=True)})

def remove_post(request):
    post_id = request.POST["post_id"]
    post = Posts.objects.get(id=post_id)
    post.delete()
    return JsonResponse({"operation":"success", "post_id":post_id})

def like(request, target, id):
    client = Client("http://127.0.0.1:8080/publish")
    if target=="post":
        print "post postan"
        post = Posts.objects.get(id=id)
        like = Likes(post=post,date_created=datetime.now(), user=request.user)
        like.save()
        likes_count = len(Likes.objects.filter(post=post))
        return JsonResponse({"status":"liked","id":"#"+target+"_"+str(id)})
    elif target=="comment":
        print "comment postan"
        post = Posts.objects.get(id=id)
        like = Likes(post=post,date_created=datetime.now(), user=request.user)
        like.save()
        likes_count = len(Likes.objects.filter(post=post))
        return JsonResponse({"status":"liked","id":"#"+target+"_"+str(id)})
    else:
        print "nepoznata naredba"
        return HttpResponseRedirect('/')


def unlike(request, target, id):
    client = Client("http://127.0.0.1:8080/publish")
    if target=="post":
        print "post postan"
        post = Posts.objects.get(id=id)
        like = Likes.objects.filter(post=post,  user=request.user)
        like.delete()
        likes_count = len(Likes.objects.filter(post=post))
        recieptant_list = SocialUser.objects.values("friends")
        print recieptant_list
        return JsonResponse({"status":"unliked","id":"#"+target+"_"+str(id)})
    elif target=="comment":
        print "comment postan"
        post = Posts.objects.get(id=id)
        like = Likes.objects.filter(post=post,  user=request.user)
        like.delete()
        likes_count = len(Likes.objects.filter(post=post))
        return JsonResponse({"status":"unliked","id":"#"+target+"_"+str(id)})
    else:
        print "nepoznata naredba"
        return HttpResponseRedirect('/')


def remove(request, target, id):
    if target=="post":
        print "post postan"
        post = Posts.objects.get(id=id)
        post.delete()
        return JsonResponse({"status":"deleted","id":"#"+target+"_"+str(id)})
    elif target=="comment":
        print "comment postan"
        post = Posts.objects.get(id=id)
        post.delete()
        return JsonResponse({"status":"deleted","id":"#"+target+"_"+str(id)})
    else:
        print "nepoznata naredba"
        return HttpResponseRedirect('/')

def search_friends(request):
    user_list = SocialUser.objects.all().exclude(user=request.user)
    userList=[]
    for user in user_list:
        auth_user = user.user
        print user.friends.filter(id=request.user.id)
        userList.append({"user_id":auth_user.id, "user_first_name":auth_user.first_name, "user_last_name": auth_user.last_name, "user_username": auth_user.username, "user_email":auth_user.email, "user_avatar":user.image.url, "allredy_friend":len(user.friends.filter(id=request.user.id))})
    return render(request, 'socialapp/friends_search.html', {"userList":userList})

def add_or_remove_friend(request, target, id):
    if target=="add":
        social_user = SocialUser.objects.get(user=request.user)
        friend = SocialUser.objects.get(user = User.objects.get(id=id))
        friend.friends.add(request.user)
        social_user.friends.add(User.objects.get(id=id))
        social_user.save()
        friend.save()
        return JsonResponse({"status":"friend_added","id":"#friend_"+str(id)})
    elif target=="remove":
        print "prijatelj maknut"
        social_user = SocialUser.objects.get(user=request.user)
        friend = SocialUser.objects.get(user = User.objects.get(id=id))
        friend.friends.remove(request.user)
        social_user.friends.remove(User.objects.get(id=id))
        social_user.save()
        friend.save()
        friend.save()
        return JsonResponse({"status":"friend_removed","id":"#friend_"+str(id)})
    else:
        print "nepoznata naredba"
        return HttpResponseRedirect('/')

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
        result = client.publish(topic="UserId_"+social_user.id, data={"event":"new_chat","chat_data":{"chat_creator_id":chat_creator.id, "chat_title": chat_title, "last_modified": last_modified}})

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
        result = client.publish(topic="UserId_"+chat_user.user.id, data={"event":"new_msg","msg_data":{"msg_sender_id":sender.id, "chat_id": chat_user.chat.id, "msg_content": message}})
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
                    return HttpResponseRedirect('/')
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
