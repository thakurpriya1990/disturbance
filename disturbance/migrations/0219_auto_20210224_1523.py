# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-02-24 07:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('disturbance', '0218_auto_20210224_1429'),
    ]

    operations = [
        migrations.AlterField(
            model_name='masterlistquestion',
            name='option',
            field=models.ManyToManyField(blank=True, null=True, to='disturbance.QuestionOption'),
        ),
    ]
