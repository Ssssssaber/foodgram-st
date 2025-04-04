# Generated by Django 5.1.7 on 2025-04-04 11:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_favoriteuserrecipes_usercart_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ingredient',
            old_name='measure',
            new_name='measurement_unit',
        ),
        migrations.RenameField(
            model_name='recipe',
            old_name='time_to_cook',
            new_name='cooking_time',
        ),
        migrations.RenameField(
            model_name='recipe',
            old_name='description',
            new_name='text',
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='picture',
        ),
        migrations.AddField(
            model_name='recipe',
            name='image',
            field=models.ImageField(default='recipes/base.png', upload_to='recipes', verbose_name='Картинка'),
        ),
    ]
