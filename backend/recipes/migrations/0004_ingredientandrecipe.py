# Generated by Django 5.1.7 on 2025-03-23 11:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_rename_ingridient_ingredient'),
    ]

    operations = [
        migrations.CreateModel(
            name='IngredientAndRecipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveIntegerField(verbose_name='')),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to='recipes.ingredient', verbose_name='')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_ingredients', to='recipes.recipe', verbose_name='')),
            ],
            options={
                'verbose_name': 'Ингредиент и рецепт',
                'verbose_name_plural': 'Ингридиенты и рецепты',
            },
        ),
    ]
