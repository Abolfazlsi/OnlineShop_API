# Generated by Django 5.1.4 on 2025-05-01 19:30

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0009_alter_discountcode_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discountcode',
            name='discount',
            field=models.SmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(90)]),
        ),
    ]
