import logging
from tinkoff.invest import Client, RequestError
from tinkoff.invest.services import MarketDataService
from tinkoff.invest.schemas import OrderDirection, OrderType, GetLastPricesRequest
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TinkoffAPI:
    def __init__(self, token: str, sandbox_mode: bool):
        self.token = token
        self.sandbox_mode = sandbox_mode
        self.client = Client(self.token)

        if self.sandbox_mode:
            logger.info("Запуск в режиме песочницы")
        else:
            logger.info("Запуск в реальном режиме")

    def get_current_price(self, figi: str) -> float:
        """Получает текущую цену актива."""
        try:
            with Client(self.token) as client:  # Обернем в with для управления соединением
                response = client.market_data.get_last_prices(figi=[figi])
                if response.last_prices:
                    return response.last_prices[0].price.units + response.last_prices[0].price.nano / 1e9
                else:
                    logging.error(f"Нет данных о цене для {figi}")
                    return 0.0
        except Exception as e:
            logging.error(f"Ошибка получения цены актива {figi}: {e}")
            return 0.0

    def place_order(self, figi: str, quantity: int, price: float, direction: OrderDirection):
        """Выставить ордер на покупку или продажу."""
        try:
            with self.client as client:
                order_id = "test_order_id"  # В реальном режиме нужно сгенерировать уникальный ID
                response = client.orders.post_order(
                    figi=figi,
                    quantity=quantity,
                    price=price,
                    direction=direction,
                    account_id="",
                    order_type=OrderType.ORDER_TYPE_LIMIT,
                    order_id=order_id
                )
                return response
        except RequestError as e:
            logger.error(f"Ошибка при выставлении ордера {figi}: {e}")
            return None

    def cancel_order(self, order_id: str):
        """Отменить ордер по его ID."""
        try:
            with self.client as client:
                client.orders.cancel_order(order_id=order_id)
                logger.info(f"Ордер {order_id} отменен")
        except RequestError as e:
            logger.error(f"Ошибка отмены ордера {order_id}: {e}")

