# Generated by Django 4.0.6 on 2024-09-06 00:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_phrase_noise'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='phrase',
            name='noise',
        ),
        migrations.RemoveField(
            model_name='phrase',
            name='que_score',
        ),
    ]
