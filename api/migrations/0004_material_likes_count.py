# Generated by Django 4.1.3 on 2022-12-04 09:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_material'),
    ]

    operations = [
        migrations.AddField(
            model_name='material',
            name='likes_count',
            field=models.IntegerField(default=0, verbose_name='Количество лайков'),
        ),
    ]
