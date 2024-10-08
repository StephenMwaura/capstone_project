# Generated by Django 5.0.7 on 2024-10-08 09:21

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Review', '0005_movie_user'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='user',
            field=models.ForeignKey(default=12, on_delete=django.db.models.deletion.CASCADE, related_name='movies', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]