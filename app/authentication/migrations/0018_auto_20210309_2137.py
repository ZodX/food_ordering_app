# Generated by Django 3.1.5 on 2021-03-09 20:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0017_auto_20210221_2047'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='customer_name',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='description',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
