import time
import csv
from bot.config import Config
from bot.grid import GridTradingBot
from bot.telegram_bot import send_telegram_message
from bot.logger import logger
from bot.storage import assets_storage, orders_storage
from datetime import datetime

bot = GridTradingBot()
open_positions = {}


def get_next_order_id():
    """Генерирует очередной порядковый номер `order_id` (1, 2, 3, ...)"""
    try:
        with open("data/orders.csv", "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)  # Пропускаем заголовки
            order_ids = [int(row[5]) for row in reader if row[5].isdigit()]
            return str(max(order_ids) + 1) if order_ids else "1"
    except FileNotFoundError:
        return "1"


def update_order_status(order_id, new_status):
    """Обновляет статус ордера в CSV"""
    updated_orders = []

    with open("data/orders.csv", "r", encoding="utf-8") as file:
        lines = file.readlines()

    for line in lines:
        data = line.strip().split(",")
        if len(data) < 7:
            continue

        if data[5] == order_id:
            data[6] = new_status  # Обновляем статус ордера
        updated_orders.append(",".join(data))

    with open("data/orders.csv", "w", encoding="utf-8") as file:
        file.write("\n".join(updated_orders) + "\n")


def main():
    logger.info(f"Бот запущен в режиме {'ТЕСТ' if Config.TRADE_MODE == 'TEST' else 'ТОРГОВЛИ'}.")
    send_telegram_message(f"✅ Бот запущен в режиме {'ТЕСТ' if Config.TRADE_MODE == 'TEST' else 'ТОРГОВЛИ'}.")

    figi = "BBG004730N88"
    lots = 1

    while True:
        price = bot.api.get_current_price(figi)
        timestamp = datetime.now().isoformat()

        if price:
            if figi in open_positions:
                buy_price, buy_order_id = open_positions[figi]
                target_price = buy_price * (1 + Config.PROFIT_PERCENT / 100)
                stop_loss_price = buy_price * (1 - Config.STOP_LOSS_PERCENT / 100)

                if price >= target_price or price <= stop_loss_price:
                    trade_type = "SELL"
                    reason = "Take-Profit" if price >= target_price else "Stop-Loss"

                    if Config.MODE == "TRADE":
                        sell_order_id = bot.api.place_order(figi, lots, trade_type, price)
                    else:
                        sell_order_id = get_next_order_id()  # Генерируем порядковый номер

                    bot.trade(figi, price, lots, trade_type)
                    logger.info(f"Продажа {figi} по {price} ({reason})")
                    send_telegram_message(f"✅ Продажа {figi} по {price} ({reason})")

                    update_order_status(buy_order_id, "FILLED")

                    orders_storage.append([figi, "Sberbank", price, trade_type, timestamp, sell_order_id, "PENDING"])
                    open_positions.pop(figi)

                else:
                    logger.info(f"Ждём {figi}: цена {price}, TP {target_price}, SL {stop_loss_price}")
            else:
                trade_type = "BUY"

                if Config.TRADE_MODE == "TRADE":
                    buy_order_id = bot.api.place_order(figi, lots, trade_type, price)
                else:
                    buy_order_id = get_next_order_id()  # Генерируем порядковый номер

                bot.trade(figi, price, lots, trade_type)
                logger.info(f"Покупка {figi} по {price}")

                open_positions[figi] = (price, buy_order_id)
                assets_storage.append([figi, "Sberbank", price, timestamp])
                orders_storage.append([figi, "Sberbank", price, trade_type, timestamp, buy_order_id, "PENDING"])

        time.sleep(Config.UPDATE_INTERVAL)


if __name__ == "__main__":
    main()
