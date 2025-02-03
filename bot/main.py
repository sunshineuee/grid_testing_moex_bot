import time
import csv
from bot.config import Config
from bot.grid import GridTradingBot
from bot.telegram_bot import send_telegram_message
from bot.logger import logger
from bot.storage import assets_storage, orders_storage
from datetime import datetime

bot = GridTradingBot()

def update_order_status(order_id, new_status):
    """Обновляет статус ордера в CSV"""
    updated_orders = []

    with open("data/orders.csv", "r", encoding="utf-8") as file:
        lines = file.readlines()

    for line in lines:
        data = line.strip().split(",")
        if len(data) < 7:
            continue  # Пропускаем строки с некорректными данными

        if data[5] == order_id:  # Если нашли нужный order_id
            data[6] = new_status  # Обновляем статус
        updated_orders.append(",".join(data))

    with open("data/orders.csv", "w", encoding="utf-8") as file:
        file.write("\n".join(updated_orders) + "\n")


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


def create_grid_orders(figi, asset_name, base_price, lots):
    """Создаёт сетку ордеров для актива, если её ещё нет"""
    try:
        with open("data/orders.csv", "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            orders = [row for row in reader if row[0] == figi]
            if orders:
                logger.info(f"Сетка ордеров для {asset_name} уже существует. Новая сетка не создаётся.")
                return  # Сетка уже создана, выходим из функции
    except FileNotFoundError:
        pass  # Если файла нет, создаём сетку с нуля

    # Создаём сетку ордеров
    for i in range(1, Config.GRID_SIZE + 1):
        buy_price = round(base_price * (1 - (Config.GRID_STEP / 100) * i), 2)
        sell_price = round(base_price * (1 + (Config.GRID_STEP / 100) * i), 2)

        buy_order_id = get_next_order_id()
        sell_order_id = get_next_order_id()

        logger.info(f"Создаём BUY-ордер на {buy_price} для {asset_name}, ID: {buy_order_id}")
        logger.info(f"Создаём SELL-ордер на {sell_price} для {asset_name}, ID: {sell_order_id}")

        orders_storage.append([figi, asset_name, buy_price, "BUY", datetime.now().isoformat(), buy_order_id, "PENDING"])
        orders_storage.append(
            [figi, asset_name, sell_price, "SELL", datetime.now().isoformat(), sell_order_id, "PENDING"])


def main():
    logger.info(f"Бот запущен в режиме {'ТЕСТ' if Config.TRADE_MODE == 'TEST' else 'ТОРГОВЛИ'}.")
    send_telegram_message(f"✅ Бот запущен в режиме {'ТЕСТ' if Config.TRADE_MODE == 'TEST' else 'ТОРГОВЛИ'}.")

    lots = 1

    for figi, asset_name in Config.FIGI_LIST.items():
        price = bot.api.get_current_price(figi)
        if price:
            logger.info(f"Проверяем существование сетки ордеров для {asset_name}")
            create_grid_orders(figi, asset_name, price, lots)

    while True:
        for figi, asset_name in Config.FIGI_LIST.items():
            price = bot.api.get_current_price(figi)
            timestamp = datetime.now().isoformat()

            if price:
                # ✅ Записываем котировку в `assets.csv`
                assets_storage.append([figi, asset_name, price, timestamp])
                logger.info(f"Записана текущая котировка: {asset_name} ({figi}) - {price}")

                with open("data/orders.csv", "r", encoding="utf-8") as file:
                    reader = csv.reader(file)
                    for row in reader:
                        if row[0] == "asset_id":  # Пропускаем заголовки
                            continue

                        if len(row) < 7:
                            logger.warning(f"Пропущена некорректная строка в orders.csv: {row}")
                            continue  # Пропускаем строки с ошибками

                        try:
                            order_price = float(row[2])  # ✅ Исправленный индекс
                            order_id = row[5]
                            order_type = row[3]
                            status = row[6]
                        except ValueError:
                            logger.error(f"Ошибка чтения строки: {row}")
                            continue  # Пропускаем ошибочные строки

                        if row[0] == figi and status == "PENDING" and (
                                (order_type == "BUY" and price <= order_price) or
                                (order_type == "SELL" and price >= order_price)
                        ):
                            logger.info(f"Исполняем {order_type}-ордер {order_id} для {asset_name} по цене {price}")
                            update_order_status(order_id, "FILLED")

                            # ✅ Создаём сразу ДВА новых ордера (BUY и SELL)
                            new_buy_price = round(price * (1 - Config.GRID_STEP / 100), 2)
                            new_sell_price = round(price * (1 + Config.GRID_STEP / 100), 2)

                            new_buy_order_id = get_next_order_id()
                            new_sell_order_id = get_next_order_id()

                            orders_storage.append(
                                [figi, asset_name, new_buy_price, "BUY", datetime.now().isoformat(), new_buy_order_id,
                                 "PENDING"])
                            orders_storage.append([figi, asset_name, new_sell_price, "SELL", datetime.now().isoformat(),
                                                   new_sell_order_id, "PENDING"])

                            logger.info(
                                f"Созданы новые ордера: BUY {new_buy_order_id} ({new_buy_price}) и SELL {new_sell_order_id} ({new_sell_price}) для {asset_name}")

        time.sleep(Config.UPDATE_INTERVAL)


if __name__ == "__main__":
    main()
