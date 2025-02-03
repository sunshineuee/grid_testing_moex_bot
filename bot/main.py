import time
import logging
from bot.config import Config
from bot.grid import GridTradingBot
from bot.telegram_bot import send_telegram_message

logging.basicConfig(level=logging.INFO)

bot = GridTradingBot()

def main():
    logging.info("Бот запущен в режиме наблюдателя.")
    send_telegram_message("✅ Бот запущен в режиме наблюдателя.")

    figi = "BBG004730N88"  # Например, FIGI акций Сбербанка
    lots = 1

    while True:
        price = bot.api.get_current_price(figi)
        if price:
            bot.trade(figi, price, lots, "buy")
            logging.info(f"Текущая цена: {price}")

        time.sleep(Config.UPDATE_INTERVAL)

if __name__ == "__main__":
    main()
