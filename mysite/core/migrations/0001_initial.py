# Generated by Django 3.2.7 on 2021-09-14 22:10

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AcmeWebhookMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('received_at', models.DateTimeField(help_text='When we received the event.')),
                ('payload', models.JSONField(default=None, null=True)),
            ],
        ),
        migrations.AddIndex(
            model_name='acmewebhookmessage',
            index=models.Index(fields=['received_at'], name='core_acmewe_receive_3bfdb8_idx'),
        ),
    ]