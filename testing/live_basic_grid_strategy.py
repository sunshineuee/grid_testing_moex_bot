from storage.dto.order import Order
from storage.storage import orders_storage
from strategy.basic_grid_strategy import Strategy
from datetime import datetime


class LiveTesting:
    def __init__(self, config):
        self.orders = {name: [] for name in config.FIGI_LIST.values()}

    def execute(self, figi_list, api):
        for figi, asset_name in figi_list.items():
            price = api.get_current_price(figi)
            self.close_orders(figi, asset_name, price)
            self.cleanup_orders(figi, asset_name, price)
            self.generate_orders(figi, asset_name, price)

    def close_orders(self, figi, asset_name, price):
        """
        Закрывает исполнившиеся ордера и отменяет встречные по `linked_id`.
        """

        open_orders = self.orders.get(asset_name, [])

        # ✅ 1. Находим исполненные ордера
        executed_orders = [
            order for order in open_orders if
            (order.type == "BUY" and price <= order.price) or
            (order.type == "SELL" and price >= order.price)
        ]

        # ✅ 2. Обновляем статус исполненных ордеров
        for order in executed_orders:
            order.status = "FILLED"
            orders_storage.update(order, "id")

        # ✅ 3. Находим встречные ордера по `linked_id`
        linked_orders = []  # ✅ Используем `list()`, а не `set()`
        for order in executed_orders:
            linked_order = next(
                (o for o in open_orders
                 if hasattr(o, "linked_id")
                 and o.linked_id == order.linked_id
                 and not o.id == order.id
                 ), None
            )
            if linked_order and linked_order not in linked_orders:  # Проверяем, чтобы не было дубликатов
                linked_order.status = "CANCELLED"
                orders_storage.update(linked_order, "id")
                linked_orders.append(linked_order)  # ✅ Добавляем в `list()`

        # ✅ 4. Обновляем `self.orders[asset_name]`
        self.orders[asset_name] = [
            order for order in open_orders if order not in executed_orders and order not in linked_orders
        ]

    def cleanup_orders(self, figi, asset_name, price):
        pass

    def generate_orders(self, figi, asset_name, price):
        strategy = Strategy(figi, asset_name)
        timestamp = datetime.now()
        new_orders = [
            Order(
                figi=o.figi,
                asset_name=o.asset_name,
                price=o.price,
                type=o.type,
                timestamp=timestamp,
                status="PENDING",
                id=o.id,
                linked_id=f"{timestamp}_{o.id}"
            )
            for o in strategy.generate_orders(price, self.orders)
        ]

        new_orders = orders_storage.extend(new_orders, "id")

        self.orders.setdefault(asset_name, []).extend(new_orders)
