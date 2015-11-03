from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, views
from socialapp.models import SocialUser, Posts, Likes
from django.db.models import Q
from datetime import datetime, timedelta
from crossbarhttp import *

def index(request):
    isAuth = False
    username = ""
    post_dict = {}
    if request.user.is_authenticated():
        social_user = request.user
        isAuth = True
        username = social_user.username
        all_posts_and_comments = Posts.objects.all().filter(Q(user=social_user) | Q(user__in=social_user.friends.all().values_list('user'))).order_by("date_created")
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
                post_dict["post_"+str(post.id)]={"postId":post.id,"post_creator_id":post.user.user.id, "post_creator_username":post.user.user.username, "post_text":post.text,"post_image":post_image,"post_likes":len(post_likes), "liked_alredy":liked_alredy, "post_comments":[], "post_date_created": post.date_created}
            else:
                post_dict["post_"+post.parent.id]["comments"].append({"commentId":post.id,"comment_creator_id":post.user.id, "comment_creator_username":post.user.username, "comment_text":post.text,"comment_image":post_image,"comment_likes":len(post_likes), "liked_alredy":liked_alredy})
    #print sorted(post_dict.values(), key=lambda k: k['post_date_created'], reverse=True)
    return render(request, 'index.html', {'user':{'is_authenticated':isAuth, 'username':username, "user_id":request.user.id}, "posts":sorted(post_dict.values(), key=lambda k: k['post_date_created'], reverse=True)})

def remove_post(request):
    post_id = request.POST["post_id"]
    post = Posts.objects.get(id=post_id)
    post.delete()
    return JsonResponse({"operation":"success", "post_id":post_id})