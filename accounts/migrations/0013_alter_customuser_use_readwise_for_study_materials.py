# Generated by Django 4.0.6 on 2024-09-08 06:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_customuser_use_readwise_for_study_materials'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='use_readwise_for_study_materials',
            field=models.BooleanField(default=False, help_text='Send study materials to <a href="https://readwise.io/" target="_blank">Readwise</a> (instead of email) if <a href="https://readwise.io/access_token" target="_blank">API key</a> is available.'),
        ),
    ]
