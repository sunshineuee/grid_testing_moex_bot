from conf.config import Config
from logs.logger import logger
from messenger.telegram_bot import send_telegram_message
from storage.dto.assets import Asset
from storage.dto.balance import Balance
from storage.dto.order import Order
from storage.storage import orders_storage, assets_storage, balance_storage
from strategy.basic_grid_strategy import Strategy
from datetime import datetime


class LiveTesting:
    def __init__(self, config):
        self.orders = {name: [] for name in config.ASSET_LIST.values()}
        self.timestamp = datetime.now()
        self.balance = 0
        self.portfolio_info = {
            figi: {"figi": figi, "name": name, "price": 0, "account": 0}
            for figi, name in config.ASSET_LIST.items()
        }
        logger.info(f"Бот запущен в режиме {'ТЕСТ' if Config.TRADE_MODE == 'TEST' else 'ТОРГОВЛИ'}.")
        send_telegram_message(f"✅ Бот запущен в режиме {'ТЕСТ' if Config.TRADE_MODE == 'TEST' else 'ТОРГОВЛИ'}.")

    def execute(self, figi_list, api):
        for figi, asset_name in figi_list.items():
            self.timestamp = datetime.now()
            price = api.get_current_price(figi)
            if price:
                assets_storage.append(Asset(figi=figi, asset_name=asset_name, price=price, timestamp=self.timestamp))
                logger.info(f"Записана текущая котировка: {asset_name} ({figi}) - {price}")
                self.portfolio_info[figi]["price"] = price
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
            logger.info(f"✅ Исполняем {order.type}-ордер для {order.asset_name} по цене {order.price}")
            self.portfolio_info[order.figi]["account"] += (1, -1)[order.type == "BUY"]
            self.balance += order.price if order.type == "BUY" else -order.price
            logger.info(f"💰 Балланс виртуального счета: {self.balance}")
            logger.info(f"📊 Стоимость активов:" + ", ".join(
                f"{info['name']}: {info['price'] * info['account']}"
                for info in self.portfolio_info.values()
            ))
            logger.info(f"📊 Итого:{sum(info['price'] * info['account'] for info in self.portfolio_info.values())+self.balance}")
            portfolio = sum(info['price'] * info['account'] for info in self.portfolio_info.values()) + self.balance
            balance_storage.append(Balance(figi=order.figi,
                                           asset_name=order.asset_name,
                                           type=order.type,
                                           timestamp=self.timestamp,
                                           id=order.id,
                                           price=order.price,
                                           account=order.price,
                                           portfolio=portfolio))

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
            logger.info(f"❌ Отменяем {order.type}-ордер для {order.asset_name} по цене {order.price}")

            # ✅ 4. Обновляем `self.orders[asset_name]`
            self.orders[asset_name] = [
                order for order in open_orders if order not in executed_orders and order not in linked_orders
            ]

    def cleanup_orders(self, figi, asset_name, price):
        pass

    def generate_orders(self, figi, asset_name, price):
        strategy = Strategy(figi, asset_name)
        new_orders = [
            Order(
                figi=o.figi,
                asset_name=o.asset_name,
                price=o.price,
                type=o.type,
                timestamp=self.timestamp,
                status="PENDING",
                id=o.id,
                linked_id=f"{self.timestamp}_{o.id}"
            )
            for o in strategy.generate_orders(price, self.orders)
        ]

        new_orders = orders_storage.extend(new_orders, "id")

        self.orders.setdefault(asset_name, []).extend(new_orders)
