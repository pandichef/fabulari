# Generated by Django 4.0.6 on 2024-09-07 19:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_customuser_last_readwise_update_articles'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='readwise_api_key',
            field=models.CharField(blank=True, help_text='Generate API key <a href="https://readwise.io/access_token" target="_blank">here</a> if you have an account.', max_length=75, null=True),
        ),
    ]
