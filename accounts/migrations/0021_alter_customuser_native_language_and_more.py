# Generated by Django 4.0.6 on 2024-09-18 01:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0020_alter_customuser_openai_llm_model_complex_tasks'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='native_language',
            field=models.CharField(choices=[('en', 'English'), ('es', 'Spanish'), ('ru', 'Russian'), ('he', 'Hebrew'), ('ar', 'Arabic'), ('zh', 'Chinese'), ('de', 'German'), ('la', 'Latin'), ('fr', 'French'), ('pt', 'Portuguese')], default='en', max_length=10, verbose_name='native language'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='working_on',
            field=models.CharField(choices=[('en', 'English'), ('es', 'Spanish'), ('ru', 'Russian'), ('he', 'Hebrew'), ('ar', 'Arabic'), ('zh', 'Chinese'), ('de', 'German'), ('la', 'Latin'), ('fr', 'French'), ('pt', 'Portuguese')], default='es', max_length=10, verbose_name='working on'),
        ),
    ]
