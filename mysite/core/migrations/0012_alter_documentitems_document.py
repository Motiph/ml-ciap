# Generated by Django 3.2.7 on 2021-11-17 03:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_documentitems'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentitems',
            name='document',
            field=models.FileField(upload_to='uploads/'),
        ),
    ]
