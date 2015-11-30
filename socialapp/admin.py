from django.contrib import admin

# Register your models here.
from .models import Posts, DataTypes, ChatMessages, Chats, SocialUser

admin.site.register(Posts)
admin.site.register(DataTypes)
admin.site.register(ChatMessages)
admin.site.register(Chats)
admin.site.register(SocialUser)