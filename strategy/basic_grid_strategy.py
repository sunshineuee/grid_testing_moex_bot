from conf.config import Config
from strategy.dto.order import Order


class Strategy:
    def __init__(self, figi, asset_name):
        self.price = None
        self.orders = None
        self.figi = figi
        self.asset_name = asset_name


    def generate_orders(self, price, orders=None):
        self.price = price
        self.orders = orders if orders is not None else []

        new_orders = []  # Общий список новых ордеров
        i = 1  # Счетчик итераций

        while len(self.orders[self.asset_name]) + len(new_orders) < Config.GRID_SIZE * 2:
            step = Config.GRID_STEP * i / 100  # Увеличиваем шаг с каждой итерацией

            new_orders.extend([
                Order(id=i,
                      figi=self.figi,
                      asset_name=self.asset_name,
                      price=round(price * (1 - step), 2),
                      type="BUY",
                      ),
                Order(id=i,
                      figi=self.figi,
                      asset_name=self.asset_name,
                      price=round(price * (1 + step), 2),
                      type="SELL",
                      )
            ])

            i += 1  # Увеличиваем счетчик


        return new_orders

