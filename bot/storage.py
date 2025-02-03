import os
import csv
from datetime import datetime

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

class Storage:
    def __init__(self, filename):
        self.filepath = os.path.join(DATA_DIR, filename)
        self.init_file()

    def init_file(self):
        """Создает файл с заголовками, если он пустой"""
        if not os.path.exists(self.filepath):
            with open(self.filepath, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                if "assets" in self.filepath:
                    writer.writerow(["asset_id", "asset_name", "price", "timestamp"])
                elif "orders" in self.filepath:
                    writer.writerow(["asset_id", "asset_name", "order_price", "order_type", "timestamp", "order_id", "status"])

    def append(self, data):
        """Добавляет строку в CSV"""
        with open(self.filepath, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(data)

# Экземпляры для работы с CSV
assets_storage = Storage("assets.csv")
orders_storage = Storage("orders.csv")

# Пример записи данных
assets_storage.append(["AAPL", "Apple Inc.", 180.5, datetime.now().isoformat()])
orders_storage.append(["AAPL", "Apple Inc.", 180.5, "BUY", datetime.now().isoformat(), "order123", "PENDING"])
