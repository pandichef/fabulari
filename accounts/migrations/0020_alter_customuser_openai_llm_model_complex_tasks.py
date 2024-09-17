# Generated by Django 4.0.6 on 2024-09-17 04:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0019_alter_customuser_openai_llm_model_complex_tasks'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='openai_llm_model_complex_tasks',
            field=models.CharField(choices=[('gpt-4o-mini', 'gpt-4o-mini (cheapest model)'), ('gpt-4o', 'gpt-4o (~30x more expensive than gpt-4o-mini)'), ('chatgpt-4o-latest', 'chatgpt-4o-latest (~30x more expensive than gpt-4o-mini)')], default='gpt-4o', help_text='Used for translations and exercise feedback.  Note that gpt-4o-mini is used for classification tasks.', max_length=100, verbose_name='OpenAI LLM Model'),
        ),
    ]
