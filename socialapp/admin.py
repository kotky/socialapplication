from django.contrib import admin

# Register your models here.
from .models import Posts, DataTypes

admin.site.register(Posts)
admin.site.register(DataTypes)