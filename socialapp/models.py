from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
# Create your models here.
class SocialUser(models.Model):
    user = models.OneToOneField(User,related_name='%(app_label)s_%(class)s_user', primary_key=True)
    image = models.ImageField(upload_to='avatar', default = 'avatar/icon-user-default.png')
    phone = models.CharField(max_length=30)
    friends = models.ManyToManyField(User,related_name='%(app_label)s_%(class)s_friend')
    def __unicode__(self):              # __unicode__ on Python 2
        return self.user.username
    def delete(self, *args, **kwargs):
        if self.image.url != '/media/avatar/icon-user-default.png':
            self.image.delete()
        super(SocialUser, self).delete(*args, **kwargs)
#user.pic.url

class Chats(models.Model):
    creator = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_user')
    date_created = models.DateTimeField('date and time created')
    title = models.CharField(max_length=200)
    last_modified = models.DateTimeField('date and time modified')
    def __unicode__(self):              # __unicode__ on Python 2
        return self.title

class DataTypes(models.Model):
    type_name = models.CharField(max_length=30)

class ChatsUsers(models.Model):
    chat = models.ForeignKey(Chats)
    user = models.ForeignKey(User)

class ChatMessages(models.Model):
    text = models.CharField(max_length=1024)
    date_pub = models.DateTimeField('date published')
    chat = models.ForeignKey(Chats)
    user = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_user')
    def __unicode__(self):              # __unicode__ on Python 2
        return self.text

class Posts(models.Model):
    user = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_user')
    date_created = models.DateTimeField('date and time created')
    type = models.ForeignKey(DataTypes, null=True)
    title = models.CharField(max_length=512, default="")
    text = models.CharField(max_length=512, default="")
    image = models.ImageField(upload_to='posts', null=True)
    parent = models.ForeignKey("self", null=True, blank = True)
    def __unicode__(self):              # __unicode__ on Python 2
        return self.text
    def delete(self, *args, **kwargs):
        self.image.delete()
        super(Posts, self).delete(*args, **kwargs)

class Likes(models.Model):
    user = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_user')
    date_created = models.DateTimeField('date and time created')
    post = models.ForeignKey(Posts)

