import time
import csv
from bot.config import Config
from bot.grid import GridTradingBot
from bot.telegram_bot import send_telegram_message
from bot.logger import logger
from bot.storage import assets_storage, orders_storage
from datetime import datetime

bot = GridTradingBot()


def get_next_order_id():
    """Генерирует порядковый номер `order_id` (1, 2, 3, ...)"""
    try:
        with open("data/orders.csv", "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)  # Пропускаем заголовки
            order_ids = [int(row[5]) for row in reader if row[5].isdigit()]
            return str(max(order_ids) + 1) if order_ids else "1"
    except FileNotFoundError:
        return "1"


def create_grid_orders(figi, base_price, lots):
    """Создаёт сетку ордеров, если её ещё нет"""
    try:
        with open("data/orders.csv", "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            orders = [row for row in reader if row[0] == figi]
            if orders:
                logger.info(f"Сетка ордеров уже существует. Новая сетка не создаётся.")
                return  # Сетка уже создана, выходим из функции
    except FileNotFoundError:
        pass  # Если файла нет, создаём сетку с нуля

    # Создаём сетку ордеров
    for i in range(1, Config.GRID_SIZE + 1):
        buy_price = round(base_price * (1 - (Config.GRID_STEP / 100) * i), 2)
        sell_price = round(base_price * (1 + (Config.GRID_STEP / 100) * i), 2)

        buy_order_id = get_next_order_id()
        sell_order_id = get_next_order_id()

        logger.info(f"Создаём BUY-ордер на {buy_price}, ID: {buy_order_id}")
        logger.info(f"Создаём SELL-ордер на {sell_price}, ID: {sell_order_id}")

        orders_storage.append([figi, "Sberbank", buy_price, "BUY", datetime.now().isoformat(), buy_order_id, "PENDING"])
        orders_storage.append(
            [figi, "Sberbank", sell_price, "SELL", datetime.now().isoformat(), sell_order_id, "PENDING"])


def main():
    logger.info(f"Бот запущен в режиме {'ТЕСТ' if Config.TRADE_MODE == 'TEST' else 'ТОРГОВЛИ'}.")
    send_telegram_message(f"✅ Бот запущен в режиме {'ТЕСТ' if Config.TRADE_MODE == 'TEST' else 'ТОРГОВЛИ'}.")

    figi = "BBG004730N88"
    lots = 1

    price = bot.api.get_current_price(figi)
    if price:
        logger.info(f"Проверяем существование сетки ордеров для {figi}")
        create_grid_orders(figi, price, lots)  # Создаём сетку только если её нет

    while True:
        price = bot.api.get_current_price(figi)
        timestamp = datetime.now().isoformat()

        if price:
            # ✅ Записываем котировку в `assets.csv`
            assets_storage.append([figi, "Sberbank", price, timestamp])
            logger.info(f"Записана текущая котировка: {figi} - {price}")

            with open("data/orders.csv", "r", encoding="utf-8") as file:
                reader = csv.reader(file)
                for row in reader:
                    if row[0] == "asset_id":
                        continue  # Пропускаем заголовки

                    order_id = row[5]
                    order_price = float(row[2])
                    order_type = row[3]
                    status = row[6]

                    if status == "PENDING" and ((order_type == "BUY" and price <= order_price) or (
                            order_type == "SELL" and price >= order_price)):
                        logger.info(f"Исполняем {order_type}-ордер {order_id} по цене {price}")
                        update_order_status(order_id, "FILLED")

                        # После исполнения создаём новый противоположный ордер
                        new_price = round(price * (1 + Config.GRID_STEP / 100), 2) if order_type == "BUY" else round(
                            price * (1 - Config.GRID_STEP / 100), 2)
                        new_order_id = get_next_order_id()
                        new_order_type = "SELL" if order_type == "BUY" else "BUY"
                        orders_storage.append(
                            [figi, "Sberbank", new_price, new_order_type, datetime.now().isoformat(), new_order_id,
                             "PENDING"])
                        logger.info(f"Создан новый {new_order_type}-ордер {new_order_id} по цене {new_price}")

        time.sleep(Config.UPDATE_INTERVAL)


if __name__ == "__main__":
    main()
