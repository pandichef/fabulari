# Generated by Django 4.0.6 on 2024-09-17 03:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_alter_phrase_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='phrase',
            name='language',
            field=models.CharField(blank=True, choices=[('en', 'English'), ('es', 'Spanish'), ('ru', 'Russian'), ('he', 'Hebrew'), ('ar', 'Arabic'), ('zh', 'Chinese'), ('de', 'German'), ('la', 'Latin'), ('fr', 'French')], help_text='"Uses your "working on" language if left blank.  See Settings.', max_length=10, verbose_name='language'),
        ),
        migrations.AlterField(
            model_name='phrase',
            name='raw_text',
            field=models.CharField(help_text='This can be in any language you choose.', max_length=255, verbose_name='Raw text'),
        ),
    ]
