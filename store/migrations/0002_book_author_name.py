# Generated by Django 4.2.7 on 2024-01-24 08:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='author_name',
            field=models.CharField(default='', max_length=255, verbose_name='Автор'),
        ),
    ]