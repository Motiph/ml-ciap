# Generated by Django 3.2.7 on 2021-09-20 19:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_tokenmercadolibre_usermercadolibre'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usermercadolibre',
            name='client_id',
            field=models.CharField(max_length=50),
        ),
    ]