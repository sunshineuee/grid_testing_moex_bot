import logging
from bot.tinkoff_api import TinkoffAPI
from tinkoff.invest.schemas import OrderDirection
from config import Config

logger = logging.getLogger(__name__)

class GridTradingBot:
    def __init__(self):
        self.api = TinkoffAPI(token=Config.TINKOFF_API_TOKEN, sandbox_mode=Config.TINKOFF_SANDBOX_MODE)
        self.trade_mode = Config.TRADE_MODE  # TEST или TRADE
        logger.info(f"Бот запущен в режиме {self.trade_mode}")

    def trade(self, figi: str, price: float, lots: int, order_type: str):
        """Выставление ордера в зависимости от режима работы бота."""
        if order_type.lower() == "buy":
            direction = OrderDirection.ORDER_DIRECTION_BUY
        elif order_type.lower() == "sell":
            direction = OrderDirection.ORDER_DIRECTION_SELL
        else:
            logger.error(f"Некорректный тип ордера: {order_type}")
            return

        if self.trade_mode == "TRADE":
            response = self.api.place_order(figi, lots, price, direction)
            if response:
                logger.info(f"Выставлен ордер: {response}")
            else:
                logger.error(f"Ошибка при выставлении ордера {order_type} {figi}")
        else:
            logger.info(f"Режим TEST: Ордера не отправляются, но записываются в историю. {order_type} {lots} {figi} по цене {price}")
