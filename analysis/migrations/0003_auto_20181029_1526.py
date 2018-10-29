# Generated by Django 2.1.1 on 2018-10-29 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0002_member_gender'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cursus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
            ],
        ),
        migrations.AddField(
            model_name='member',
            name='subscriptions',
            field=models.ManyToManyField(related_name='members', to='analysis.Cursus'),
        ),
    ]
