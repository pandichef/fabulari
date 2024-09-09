# Generated by Django 4.0.6 on 2024-09-09 04:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0015_customuser_retrieve_native_language_from_readwise'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='openai_llm_model_complex_tasks',
            field=models.CharField(choices=[('gpt-4o-mini', 'gpt-4o-mini (cheapest model)'), ('gpt-4o', 'gpt-4o (~30x more expensive than gpt-4o-mini)'), ('chatgpt-4o-latest', 'chatgpt-4o-latest (~30x more expensive than gpt-4o-mini)')], default='gpt-4o-mini', help_text='Used for creating study materials and translation feedback.  Cost estimates are as of September 2024.', max_length=100, verbose_name='OpenAI LLM Model'),
        ),
    ]
