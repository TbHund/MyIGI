# Generated by Django 5.2.1 on 2025-05-29 11:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_remove_roomcategory_price_per_night_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='promotion',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.promotion', verbose_name='Использованный промокод'),
        ),
    ]
