# Generated by Django 4.2.7 on 2024-02-01 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_alter_userbookrelationship_rate'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='reating',
            field=models.DecimalField(decimal_places=2, default=None, max_digits=3, null=True, verbose_name='рейтинг книги'),
        ),
    ]
