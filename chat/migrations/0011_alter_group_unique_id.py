# Generated by Django 5.0.1 on 2024-01-22 16:56

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0010_group_unique_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='unique_id',
            field=models.UUIDField(blank=True, default=uuid.uuid4, null=True, unique=True),
        ),
    ]