from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, views
from socialapp.models import SocialUser, Posts, Likes
from django.db.models import Q
from datetime import datetime
from time import mktime
from crossbarhttp import *

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
    return render(request, 'index.html', {'user':{'is_authenticated':isAuth, 'username':username, "user_id":request.user.id}, "posts":sorted(post_dict.values(), key=lambda k: k['date_created_ms'], reverse=True)})

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

def publish_post(request):
    client = Client("http://127.0.0.1:8080/publish")
    post = Posts(user=request.user, date_created = datetime.now(), text=request.POST["text"])
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
        result = client.publish("User_"+str(user.id), {"event":"post_added","data":{"type": "post", "id":post.id,"creator_id":post.user.id, "creator_username":post.user.username, "text":post.text,"image":post_image, "date_created_ms": datetime_to_ms_str(post.date_created),"date_created":post.date_created.strftime("%A, %d. %B %Y %H:%M")}})
    result = client.publish("User_"+str(request.user.id), {"event":"post_added","data":{"type": "post", "id":post.id,"creator_id":post.user.id, "creator_username":post.user.username, "text":post.text,"image":post_image, "date_created_ms": datetime_to_ms_str(post.date_created),"date_created":post.date_created.strftime("%A, %d. %B %Y %H:%M")}})
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
    return JsonResponse({"status":"comment_added","id":request.POST["post_id"]})