# Generated by Django 3.1.5 on 2021-03-09 20:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0018_auto_20210309_2137'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='customer_name',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='description',
            field=models.CharField(default='no_message', max_length=200),
        ),
    ]
