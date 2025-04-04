# Generated by Django 5.1.7 on 2025-04-01 07:26

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_alter_recipe_ingridients'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Дата создания'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='recipe',
            name='picture',
            field=models.ImageField(default='media/base.png', upload_to='images', verbose_name='Картинка'),
        ),
    ]
