# Generated by Django 4.1.5 on 2023-01-23 13:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MainApp', '0027_order_cart'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='description',
        ),
    ]