# Generated by Django 3.2.7 on 2021-10-11 22:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20211005_1413'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderItemsMercadoLibre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pack_id_mercadolibre', models.CharField(max_length=70)),
                ('sending', models.BooleanField(default=False)),
                ('received_at', models.DateTimeField(help_text='When we received the event.')),
            ],
        ),
        migrations.AddField(
            model_name='itemsellmercadolibre',
            name='order_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.orderitemsmercadolibre'),
        ),
    ]
