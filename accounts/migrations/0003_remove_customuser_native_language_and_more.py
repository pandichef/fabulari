# Generated by Django 4.0.6 on 2024-09-05 00:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_customuser_native_language_customuser_working_on'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='native_language',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='working_on',
        ),
    ]
