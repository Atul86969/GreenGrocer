# Generated by Django 5.0.2 on 2024-03-18 15:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('FreshFruits', '0004_orderupdate'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='catg',
            new_name='category',
        ),
    ]
