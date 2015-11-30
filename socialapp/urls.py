from django.conf.urls import include, url
from socialapp import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login_user, name='login'),
    url(r'^logout/$', views.logout_user, name='logout'),
    url(r'^password_change/$', auth_views.password_change, name='password_change'),
    url(r'^password_reset/$', auth_views.password_reset, name='auth_password_reset'),
    url(r'^register/$', views.register, name='registration_register'),
    url(r'^send/post/$', views.publish_post, name='publish_post'),
    url(r'^send/comment/$', views.publish_comment, name='publish_comment'),
    url(r'^post/remove/$', views.remove_post, name='remove_post'),
    url(regex=r'^like/(?P<target>\w{1,50})/(?P<id>\w{1,50})/$', view=views.like, name='like'),
    url(regex=r'^unlike/(?P<target>\w{1,50})/(?P<id>\w{1,50})/$', view=views.unlike, name='unlike'),
    url(regex=r'^remove/(?P<target>\w{1,50})/(?P<id>\w{1,50})/$', view=views.remove, name='remove'),
    url(r'^friends/search/$', views.search_friends, name='friends_search'),
    url(r'^friends/filter/$', views.filter_friends, name='friends_filter'),
    url(r'^friends/(?P<target>\w{1,50})/(?P<id>\w{1,50})/$', views.add_or_remove_friend, name='friend_add_remove')
]