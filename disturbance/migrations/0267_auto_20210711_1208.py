# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-07-11 04:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('disturbance', '0266_auto_20210708_1640'),
    ]

    operations = [
        migrations.AddField(
            model_name='apiarysiteonapproval',
            name='approval_cpc_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='apiarysiteonapproval',
            name='approval_minister_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='apiarysiteonapproval',
            name='batch_no',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AddField(
            model_name='apiarysiteonapproval',
            name='catchment',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AddField(
            model_name='apiarysiteonapproval',
            name='cog',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AddField(
            model_name='apiarysiteonapproval',
            name='dra_permit',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='apiarysiteonapproval',
            name='forest_block',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AddField(
            model_name='apiarysiteonapproval',
            name='map_ref',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AddField(
            model_name='apiarysiteonapproval',
            name='roadtrack',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AddField(
            model_name='apiarysiteonapproval',
            name='zone',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
    ]