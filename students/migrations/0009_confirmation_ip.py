# Generated by Django 2.2.5 on 2019-09-18 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0008_auto_20190916_2152'),
    ]

    operations = [
        migrations.AddField(
            model_name='confirmation',
            name='ip',
            field=models.GenericIPAddressField(default='127.0.0.1'),
            preserve_default=False,
        ),
    ]