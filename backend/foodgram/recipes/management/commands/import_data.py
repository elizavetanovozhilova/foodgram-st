import json
import os
from pathlib import Path

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):

    help = 'Импорт ингредиентов'

    def handle(self, *args, **options):
        # Получаем путь к файлу ingredients.json
        # В Docker контейнере файл находится в /app/ingredients.json
        # В локальной разработке - в ../data/ingredients.json
        if os.path.exists('/app/ingredients.json'):
            # Docker контейнер
            ingredients_file = '/app/ingredients.json'
        else:
            # Локальная разработка
            base_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
            ingredients_file = base_dir / 'data' / 'ingredients.json'

        with open(ingredients_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        for note in data:
            try:
                Ingredient.objects.get_or_create(**note)
                print(f"{note['name']} в базе")
            except Exception as error:
                print(f"Ошибка при добавлении {note['name']}.\n"
                      f"Текст - {error}")

        print('Загрузка ингредиентов завершена')