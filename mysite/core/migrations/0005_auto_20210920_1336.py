# Generated by Django 3.2.7 on 2021-09-20 20:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_tokenmercadolibre_received_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tokenmercadolibre',
            name='expires_in',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='tokenmercadolibre',
            name='user_id',
            field=models.CharField(max_length=50),
        ),
    ]
