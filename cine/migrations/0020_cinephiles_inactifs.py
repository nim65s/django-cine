# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-10 21:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cine', '0019_cinephile_ordering'),
    ]

    operations = [
        migrations.AddField(
            model_name='cinephile',
            name='actif',
            field=models.BooleanField(default=True),
        ),
    ]
