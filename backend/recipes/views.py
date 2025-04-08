from django.shortcuts import get_object_or_404, redirect

from .models import Recipe


def get_recipe_link(request, recipe_id):
    get_object_or_404(Recipe, pk=recipe_id)
    return redirect(f'/recipes/{recipe_id}')
