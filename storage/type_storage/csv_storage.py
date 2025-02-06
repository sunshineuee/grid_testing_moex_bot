import csv
import os
import uuid
from typing import List


class CSVStorage:
    def __init__(self, filename, fields: List[str]):
        self.filepath = os.path.join("storage", filename)  # storage_name = "orders.csv"
        self.fields = fields
        self.init_file()

    def init_file(self):
        """Создает файл, если его нет"""
        if not os.path.exists(self.filepath):
            with open(self.filepath, mode="w", encoding="utf-8", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=self.fields)
                writer.writeheader()

    def update(self, data_object, filter_field: str):
        """
        Обновляет запись в CSV по заданному полю отбора.

        :param data_object: объект с новыми данными
        :param filter_field: поле, по которому ищем строку
        """
        filter_value = getattr(data_object, filter_field, None)
        if filter_value is None:
            return {"status": "error", "message": f"Объект не содержит поле {filter_field}"}

        updated_rows = []
        updated = False

        with open(self.filepath, mode="r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)

            for row in reader:
                if row.get(filter_field) == str(filter_value):  # Сравниваем значения
                    # ✅ Обновляем всю строку, используя данные из переданного объекта
                    for field in self.fields:
                        if hasattr(data_object, field):  # Проверяем, есть ли поле у объекта
                            row[field] = str(getattr(data_object, field))  # Преобразуем в строку
                    updated = True
                updated_rows.append(row)

        if updated:
            with open(self.filepath, mode="w", encoding="utf-8", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=self.fields)
                writer.writeheader()
                writer.writerows(updated_rows)

        return {"status": "updated" if updated else "not_found", "filter_field": filter_field,
                "filter_value": filter_value}

    def extend(self, data_objects: List, index_field: str = None):

        processed_objects = []  # Список обработанных объектов

        for obj in data_objects:
            # ✅ Если передан `index_field`, заменяем его уникальным значением
            if index_field and hasattr(obj, index_field):
                setattr(obj, index_field, self.generate_unique_id(index_field))

            processed_objects.append(obj)

        # ✅ Записываем в CSV динамически по `self.fields`
        with open(self.filepath, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=self.fields)

            for obj in processed_objects:
                row = {field: str(getattr(obj, field, "")) for field in self.fields}  # Динамическое формирование строки
                writer.writerow(row)

        return processed_objects

    def load_existing_ids(self, index_field: str) -> set:

        existing_ids = set()
        try:
            with open(self.filepath, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if index_field in row:
                        existing_ids.add(row[index_field])
        except FileNotFoundError:
            pass  # Если файл не существует, просто возвращаем пустое множество
        return existing_ids

    def generate_unique_id(self, index_field: str) -> str:

        existing_ids = self.load_existing_ids(index_field)
        while True:
            new_id = str(uuid.uuid4())  # Генерируем уникальный ID
            if new_id not in existing_ids:
                return new_id
