# Generated by Django 2.2.4 on 2019-08-09 13:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('students', '0003_auto_20190809_1400'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentMeta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_student', models.BooleanField()),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='studentmeta', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]