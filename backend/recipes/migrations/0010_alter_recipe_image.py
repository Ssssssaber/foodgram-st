# Generated by Django 5.1.7 on 2025-04-04 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0009_remove_ingredient_u_ingredient_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(upload_to='recipes', verbose_name='Картинка'),
        ),
    ]
