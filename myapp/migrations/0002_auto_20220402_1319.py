# Generated by Django 3.2.12 on 2022-04-02 09:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='qbodetails',
            name='access_token',
            field=models.CharField(max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='qbodetails',
            name='id_token',
            field=models.CharField(max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='qbodetails',
            name='refresh_token',
            field=models.CharField(max_length=250, null=True),
        ),
    ]
