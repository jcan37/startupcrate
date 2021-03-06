# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-08 03:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipient_name', models.CharField(max_length=64)),
                ('stripe_customer', models.CharField(max_length=32, null=True)),
                ('ship_address', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Address')),
            ],
        ),
    ]
