from dataclasses import fields
from typing import List, Type

from storage.dto.balance import Balance
from storage.dto.order import Order
from conf.config import Config
from storage.dto.assets import Asset


class Storage:
    """Менеджер хранилища, автоматически выбирающий CSV или SQL"""

    def __init__(self, storage_name: str, data_class: Type):
        """storage_name — это имя файла (для CSV) или таблицы (для SQL)"""
        self.storage_type = Config.STORAGE_TYPE
        self.data_class = data_class

        self.fields = [field.name for field in fields(self.data_class)]

        if self.storage_type == "CSV":
            from storage.type_storage.csv_storage import CSVStorage
            self.storage = CSVStorage(storage_name, self.fields)  # storage_name = "orders.csv"
        elif self.storage_type == "SQL":
            from storage.type_storage.sql_storage import SQLStorage
            self.storage = SQLStorage(storage_name, data_class)  # storage_name = "orders"
        else:
            raise ValueError("Некорректный тип хранилища! Используйте 'CSV' или 'SQL'.")

    def update(self, data_object, filter_field: str):
        """Обновляет поле в хранилище"""
        self.storage.update(data_object, filter_field)

    def insert(self, data: dict):
        """Добавляет новую запись"""
        self.storage.insert(data)

    def delete(self, order_id: str):
        """Удаляет запись по ID"""
        self.storage.delete(order_id)

    def fetch(self, order_id: str) -> dict:
        """Извлекает запись по ID"""
        return self.storage.fetch(order_id)

    def extend(self, data_objects: List, index_field: str = None):
        return self.storage.extend(data_objects, index_field)

    def append(self, data_object, index_field: str = None):
        return self.storage.append(data_object, index_field)
# Экземпляры для работы с CSV
assets_storage = Storage("data/assets.csv", Asset)
orders_storage = Storage("data/orders.csv", Order)
balance_storage = Storage("data/balance.csv", Balance)


