# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-07-08 08:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('disturbance', '0264_auto_20210708_1626'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='apiarysiteonproposal',
            name='dra_permit',
        ),
    ]