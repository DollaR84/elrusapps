# Generated by Django 2.0.6 on 2020-05-09 17:54

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Subscribers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subscriber', models.EmailField(max_length=254)),
                ('vodokanal', models.BooleanField(default=False)),
                ('weather', models.BooleanField(default=False)),
            ],
        ),
    ]