from json import loads

import os
from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Загрузка ингредиентов из .json файла"

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str)

    def handle(self, *args, **kwargs):
        filename = kwargs['json_file']
        try:
            json_file = os.path.join(
                settings.BASE_DIR,
                'example_data',
                filename
            )
            with open(json_file, "r", encoding="utf-8") as file:
                ingredient_list = loads(file.read())

                for ingredient in ingredient_list:
                    Ingredient.objects.create(
                        name=ingredient["name"],
                        measurement_unit=ingredient["measurement_unit"]
                    )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Импортировано {len(ingredient_list)} ингридиентов"
                    )
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f"Ошибка: {e}"
                )
            )
