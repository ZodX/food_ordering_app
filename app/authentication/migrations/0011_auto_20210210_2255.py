# Generated by Django 3.1.5 on 2021-02-10 21:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0010_cart'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='customer',
        ),
        migrations.AddField(
            model_name='cart',
            name='user_id',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.DeleteModel(
            name='Customer',
        ),
    ]
