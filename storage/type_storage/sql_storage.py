import sqlite3

class SQLStorage:
    def __init__(self, table_name="orders", db_path="storage/orders.db"):
        self.db_path = db_path
        self.table_name = table_name  # storage_name = "orders"
        self.init_db()

    def init_db(self):
        """Создает таблицу, если ее нет"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    order_id TEXT PRIMARY KEY,
                    order_type TEXT,
                    status TEXT,
                    price REAL
                )
            """)
            conn.commit()

    def update(self, order):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = f"UPDATE {self.table_name} SET {field} = ? WHERE order_id = ?"
            cursor.execute(query, (new_value, order_id))
            conn.commit()
    def extend(self,):
        pass