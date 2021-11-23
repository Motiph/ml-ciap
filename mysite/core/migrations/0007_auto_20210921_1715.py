# Generated by Django 3.2.7 on 2021-09-22 00:15

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_itemsellmercadolibre'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemsellmercadolibre',
            name='payment_id',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='itemsellmercadolibre',
            name='received_at',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='When we received the event.'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='itemsellmercadolibre',
            name='item_id_mercadolibre',
            field=models.CharField(max_length=300),
        ),
    ]
