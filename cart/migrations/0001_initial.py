# Generated by Django 5.1.3 on 2024-11-22 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DiscountCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20)),
                ('discount', models.SmallIntegerField(default=0)),
                ('quantity', models.IntegerField(default=1)),
            ],
        ),
    ]
