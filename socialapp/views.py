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
from time import mktime

def datetime_to_ms_str(dt):
    return str(mktime(dt.timetuple()))

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
                post_dict["post_"+str(post.id)]={"id":post.id,"creator_id":post.user.id, "creator_username":post.user.username, "text":post.text,"image":post_image,"likes_count":len(post_likes), "liked_alredy":liked_alredy, "comments":[], "date_created_ms": datetime_to_ms_str(post.date_created),"date_created":post.date_created.strftime("%A, %d. %B %Y %H:%M")}
            else:
                post_dict["post_"+str(post.parent.id)]["comments"].append({"id":post.id,"creator_id":post.user.id, "creator_username":post.user.username, "creator_image":SocialUser.objects.get(user=post.user).image.url, "text":post.text,"image":post_image,"likes_count":len(post_likes), "liked_alredy":liked_alredy, "date_created_ms": datetime_to_ms_str(post.date_created), "date_created":post.date_created.strftime("%A, %d. %B %Y %H:%M")})
    #print sorted(post_dict.values(), key=lambda k: k['post_date_created'], reverse=True)
    return render(request, 'index.html', {'user':{'is_authenticated':isAuth, 'username':username, "user_id":request.user.id}, "posts":sorted(post_dict.values(), key=lambda k: k['date_created'], reverse=True)})

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
        likes_count = len(Likes.objects.filter(post=post).distinct())
        recieptant_list = SocialUser.objects.get(user=request.user).friends.distinct()
        print recieptant_list
        for user in recieptant_list:
            result = client.publish("User_"+str(user.id), {"event":"like_update","data":{"type":target, "post_id":id, "like_count": likes_count}})
        result = client.publish("User_"+str(request.user.id), {"event":"like_update","data":{"type":target, "post_id":id, "like_count": likes_count}})
            #result = client.publish("User_"+str(user.id), "dataaa")
        return JsonResponse({"status":"liked","id":"#"+target+"_"+str(id)})
    elif target=="comment":
        print "comment postan"
        post = Posts.objects.get(id=id)
        like = Likes(post=post,date_created=datetime.now(), user=request.user)
        like.save()
        likes_count = len(Likes.objects.filter(post=post).distinct())
        recieptant_list = SocialUser.objects.get(user=request.user).friends.distinct()
        print recieptant_list
        for user in recieptant_list:
            result = client.publish("User_"+str(user.id), {"event":"like_update","data":{"type":target, "post_id":id, "like_count": likes_count}})
        result = client.publish("User_"+str(request.user.id), {"event":"like_update","data":{"type":target, "post_id":id, "like_count": likes_count}})
            #result = client.publish("User_"+str(user.id), "dataaa")
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
        likes_count = len(Likes.objects.filter(post=post).distinct())
        recieptant_list = SocialUser.objects.get(user=request.user).friends.distinct()
        print recieptant_list
        for user in recieptant_list:
            result = client.publish("User_"+str(user.id), {"event":"like_update","data":{"type":target, "post_id":id, "like_count": likes_count}})
        result = client.publish("User_"+str(request.user.id), {"event":"like_update","data":{"type":target, "post_id":id, "like_count": likes_count}})
            #result = client.publish("User_"+str(user.id), "dataaa")
        return JsonResponse({"status":"unliked","id":"#"+target+"_"+str(id)})
    elif target=="comment":
        print "comment postan"
        post = Posts.objects.get(id=id)
        like = Likes.objects.filter(post=post,  user=request.user)
        like.delete()
        likes_count = len(Likes.objects.filter(post=post).distinct())
        recieptant_list = SocialUser.objects.get(user=request.user).friends.distinct()
        print recieptant_list
        for user in recieptant_list:
            result = client.publish("User_"+str(user.id), {"event":"like_update","data":{"type":target, "post_id":id, "like_count": likes_count}})
        result = client.publish("User_"+str(request.user.id), {"event":"like_update","data":{"type":target, "post_id":id, "like_count": likes_count}})
            #result = client.publish("User_"+str(user.id), "dataaa")
        return JsonResponse({"status":"unliked","id":"#"+target+"_"+str(id)})
    else:
        print "nepoznata naredba"
        return HttpResponseRedirect('/')


def remove(request, target, id):
    client = Client("http://127.0.0.1:8080/publish")
    if target=="post":
        print "post postan"
        post = Posts.objects.get(id=id)
        post.delete()
        recieptant_list = SocialUser.objects.get(user=request.user).friends.distinct()
        print recieptant_list
        for user in recieptant_list:
            result = client.publish("User_"+str(user.id), {"event":"post_removed","data":{"type":target, "post_id":id}})
        return JsonResponse({"status":"deleted","id":"#"+target+"_"+str(id)})
    elif target=="comment":
        print "comment postan"
        post = Posts.objects.get(id=id)
        post.delete()
        recieptant_list = SocialUser.objects.get(user=request.user).friends.distinct()
        print recieptant_list
        for user in recieptant_list:
            result = client.publish("User_"+str(user.id), {"event":"post_removed","data":{"type":target, "post_id":id}})
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
        return JsonResponse({"status":"friend_added","id":"#friend_"+str(id)})
    elif target=="remove":
        print "prijatelj maknut"
        social_user = SocialUser.objects.get(user=request.user)
        friend = SocialUser.objects.get(user = User.objects.get(id=id))
        friend.friends.remove(request.user)
        social_user.friends.remove(User.objects.get(id=id))
        return JsonResponse({"status":"friend_removed","id":"#friend_"+str(id)})
    else:
        print "nepoznata naredba"
        return HttpResponseRedirect('/')

def register(request):
    if request.method == "POST":
        formUser = RegistrationFormUser(data = request.POST.copy())
        formSocialUser = RegistrationFormSocialUser(data = request.POST.copy())
        password_value = ""
        if formUser.is_valid() and formSocialUser.is_valid():
            registrationUser= formUser.save()
            password_value = registrationUser.password
            registrationUser.set_password(registrationUser.password)
            registrationUser.save()
            registrationSocialUser= formSocialUser.save(commit=False)
            registrationSocialUser.user = registrationUser
            registrationSocialUser.save()
            send_mail("Success registration on Django Social App", "Bravo, login data: username: "+registrationUser.username+", password: "+ password_value, None, [registrationUser.email], fail_silently=False)
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
        result = client.publish(topic="User_"+social_user.id, data={"event":"new_chat","chat_data":{"chat_creator_id":chat_creator.id, "chat_title": chat_title, "last_modified": last_modified}})

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
        result = client.publish(topic="User_"+chat_user.user.id, data={"event":"new_msg","msg_data":{"msg_sender_id":sender.id, "chat_id": chat_user.chat.id, "msg_content": message}})
    chat_message = ChatMessages(text = message, date_pub = datetime.now(), chat = chat, user = sender)
    chat_message.save()

def publish_post(request):
    client = Client("http://127.0.0.1:8080/publish")
    post = Posts(user=request.user, date_created = datetime.now(), text=request.POST["text"])
    post_image_url = ""
    if len(request.FILES) > 0:
        post.image = request.FILES["image"]
        post.save()
        post_image_url = post.image.url
    else:
        post.save()
    recieptant_list = SocialUser.objects.get(user=request.user).friends.distinct()
    print recieptant_list
    for user in recieptant_list:
        result = client.publish("User_"+str(user.id), {"event":"post_added","data":{"type": "post", "creator_id":request.user.id, "creator_username":request.user.username, "text":post.text, "id":post.id, "date_created":datetime_to_ms_str(post.date_created), "image_url": post_image_url}})
    result = client.publish("User_"+str(request.user.id),  {"event":"post_added","data":{"type": "post", "creator_id":request.user.id, "creator_username":request.user.username, "text":post.text, "id":post.id, "date_created":datetime_to_ms_str(post.date_created), "image_url": post_image_url}})
    return JsonResponse({"status":"post_added","id":post.id})

def publish_comment(request):
    client = Client("http://127.0.0.1:8080/publish")
    post = Posts(user=request.user, date_created = datetime.now(), text=request.POST["text"], parent=Posts.objects.get(id=request.POST["post_id"]))
    post_image = ""
    if len(request.FILES) > 0:
        post.image = request.FILES["image"]
        post.save()
        post_image = post.image.url
    else:
        post.save()
    recieptant_list = SocialUser.objects.get(user=request.user).friends.distinct()
    print recieptant_list
    for user in recieptant_list:
        result = client.publish("User_"+str(user.id), {"event":"post_added","data":{"type": "comment","post_id":request.POST["post_id"], "id":post.id,"creator_id":post.user.id, "creator_username":post.user.username, "creator_image":SocialUser.objects.get(user=post.user).image.url, "text":post.text,"image":post_image, "date_created_ms": datetime_to_ms_str(post.date_created), "date_created":post.date_created.strftime("%A, %d. %B %Y %H:%M")}})
    result = client.publish("User_"+str(request.user.id),  {"event":"post_added","data":{"type": "comment","post_id":request.POST["post_id"], "id":post.id,"creator_id":post.user.id, "creator_username":post.user.username, "creator_image":SocialUser.objects.get(user=post.user).image.url, "text":post.text,"image":post_image, "date_created_ms": datetime_to_ms_str(post.date_created), "date_created":post.date_created.strftime("%A, %d. %B %Y %H:%M")}})
    return JsonResponse({"status":"comment_added","id":post.id})

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
