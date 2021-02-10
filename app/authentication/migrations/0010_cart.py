# Generated by Django 3.1.5 on 2021-02-10 21:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0009_restaurant_owner_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='authentication.customer')),
                ('food', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='authentication.food')),
            ],
        ),
    ]
