# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('socialapp', '0002_auto_20151103_1433'),
    ]

    operations = [
        migrations.AlterField(
            model_name='socialuser',
            name='friends',
            field=models.ManyToManyField(related_name='socialuser_friend', to=settings.AUTH_USER_MODEL),
        ),
    ]
