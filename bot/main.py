import time
from bot.config import Config
from bot.grid import GridTradingBot
from bot.telegram_bot import send_telegram_message
from bot.logger import logger  # Используем новый модуль логирования
from bot.storage import assets_storage, orders_storage  # Работа с CSV
from datetime import datetime

bot = GridTradingBot()

def main():
    logger.info("Бот запущен в режиме наблюдателя.")
    send_telegram_message("✅ Бот запущен в режиме наблюдателя.")

    figi = "BBG004730N88"  # Например, FIGI акций Сбербанка
    lots = 1

    while True:
        price = bot.api.get_current_price(figi)
        timestamp = datetime.now().isoformat()

        if price:
            bot.trade(figi, price, lots, "buy")
            logger.info(f"Текущая цена: {price}")

            # Сохраняем цену актива в CSV
            assets_storage.append([figi, "Sberbank", price, timestamp])

            # Сохраняем информацию о выставленном ордере (пример)
            orders_storage.append([figi, "Sberbank", price, "BUY", timestamp, "order123", "PENDING"])

        time.sleep(Config.UPDATE_INTERVAL)

if __name__ == "__main__":
    main()
