# Generated by Django 3.1.5 on 2021-02-07 15:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0003_customer_address'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Menu',
        ),
    ]