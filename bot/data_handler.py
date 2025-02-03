import csv
import os
from datetime import datetime
from bot.config import Config


def save_asset(figi, name, price):
    """ Сохраняет историю котировок в CSV. """
    file = Config.ASSET_HISTORY_FILE
    write_header = not os.path.exists(file)

    with open(file, mode="a", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["figi", "name", "price", "timestamp"])
        writer.writerow([figi, name, price, datetime.now()])


def save_order(figi, price, order_type, order_id):
    """ Сохраняет историю ордеров в CSV. """
    file = Config.ORDER_HISTORY_FILE
    write_header = not os.path.exists(file)

    with open(file, mode="a", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["figi", "price", "type", "timestamp", "order_id"])
        writer.writerow([figi, price, order_type, datetime.now(), order_id])
