# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatMessages',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.CharField(max_length=1024)),
                ('date_pub', models.DateTimeField(verbose_name=b'date published')),
            ],
        ),
        migrations.CreateModel(
            name='Chats',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_created', models.DateTimeField(verbose_name=b'date and time created')),
                ('title', models.CharField(max_length=200)),
                ('last_modified', models.DateTimeField(verbose_name=b'date and time modified')),
            ],
        ),
        migrations.CreateModel(
            name='ChatsUsers',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('chat', models.ForeignKey(to='socialapp.Chats')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DataTypes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type_name', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Likes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_created', models.DateTimeField(verbose_name=b'date and time created')),
            ],
        ),
        migrations.CreateModel(
            name='Posts',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_created', models.DateTimeField(verbose_name=b'date and time created')),
                ('text', models.CharField(max_length=512)),
                ('image', models.ImageField(null=True, upload_to=b'posts')),
                ('parent', models.ForeignKey(blank=True, to='socialapp.Posts', null=True)),
                ('type', models.ForeignKey(to='socialapp.DataTypes', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SocialUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', models.ImageField(default=b'avatar/icon-user-default.png', upload_to=b'avatars')),
                ('phone', models.CharField(max_length=30)),
                ('friends', models.ManyToManyField(related_name='socialuser_friend', to=settings.AUTH_USER_MODEL)),
                ('user', models.OneToOneField(related_name='socialuser_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='likes',
            name='post',
            field=models.ForeignKey(to='socialapp.Posts'),
        ),
        migrations.AddField(
            model_name='likes',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='chatmessages',
            name='chat',
            field=models.ForeignKey(to='socialapp.Chats'),
        ),
        migrations.AddField(
            model_name='chatmessages',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
