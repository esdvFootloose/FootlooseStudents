# Generated by Django 2.2.4 on 2019-08-09 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0004_studentmeta'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentmeta',
            name='userid',
            field=models.IntegerField(default=-1),
            preserve_default=False,
        ),
    ]
