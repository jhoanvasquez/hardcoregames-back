# Generated by Django 4.2.5 on 2023-09-09 04:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user_customized',
            name='phone_number',
            field=models.CharField(max_length=20),
        ),
    ]
