import logging
from tinkoff.invest import Client, RequestError, TradeInstrument, MarketDataRequest, SubscribeTradesRequest, SubscriptionAction
from tinkoff.invest.sandbox.client import SandboxClient
from tinkoff.invest.schemas import OrderDirection, OrderType

from conf.config import Config
from logs.logger import logger
from storage.dto.market_data import MarketData

import pandas as pd
import time


class TinkoffAPI:
    def __init__(self):
        self.token = Config.TINKOFF_API_TOKEN
        self.sandbox_mode = Config.TINKOFF_SANDBOX_MODE
        if self.sandbox_mode:
            self.client = SandboxClient(self.token)  # Используем песочницу
        else:
            self.client = Client(self.token)
        if self.sandbox_mode:
            logger.info("⚠️ Запуск Тиньков API в режиме песочницы")
        else:
            logger.info("🛑 Запуск Тиньков API в реальном режиме")

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

    def get_live_market_data(self, figi) -> MarketData:
        """Собирает Live-данные с Tinkoff API и возвращает объект LiveMarketData"""
        with Client(self.token) as client:
            timestamp = pd.Timestamp.now()

            # 🟢 1. Получаем последнюю цену
            last_price_response = client.market_data.get_last_prices()
            last_price = None
            for price in last_price_response.last_prices:
                if price.figi == figi:
                    last_price = price.price.units + price.price.nano / 1e9
                    break

            # 🟢 2. Получаем стакан заявок (Order Book)
            order_book_response = client.market_data.get_order_book(figi=figi, depth=10)
            bids = order_book_response.bids
            asks = order_book_response.asks

            best_bid = bids[0].price.units + bids[0].price.nano / 1e9 if bids else last_price
            best_ask = asks[0].price.units + asks[0].price.nano / 1e9 if asks else last_price
            spread = best_ask - best_bid if best_bid and best_ask else 0
            bid_size = sum([bid.quantity for bid in bids]) if bids else 0
            ask_size = sum([ask.quantity for ask in asks]) if asks else 0

            # 🟢 3. Получаем последнюю 5-минутную свечу
            candles_response = client.market_data.get_candles(
                figi=figi,
                from_=timestamp - pd.Timedelta(minutes=30),  # Даем запас 10 минут
                to=timestamp,
                interval=1
            )

            if candles_response.candles:
                last_candle = candles_response.candles[-1]
                open_price = last_candle.open.units + last_candle.open.nano / 1e9
                high_price = last_candle.high.units + last_candle.high.nano / 1e9
                low_price = last_candle.low.units + last_candle.low.nano / 1e9
                close_price = last_candle.close.units + last_candle.close.nano / 1e9
                volume = last_candle.volume
            else:
                open_price = high_price = low_price = close_price = last_price
                volume = 0

            # 📌 Создаем объект MarketData

            # 🟢 4. Получаем последнюю сделку
            trade_price, trade_volume = self.get_trades(figi)

            # 🟢 5. Рассчитываем индикаторы RSI, ATR, MACD
            rsi, atr, macd = self.calculate_indicators(candles_response.candles)

            live_data = MarketData(
                timestamp=timestamp,
                open=open_price,
                high=high_price,
                low=low_price,
                close=close_price,
                volume=volume,
                last_price=last_price,
                bid=best_bid,
                ask=best_ask,
                spread=spread,
                bid_size=bid_size,
                ask_size=ask_size,
                trade_price=trade_price,
                trade_volume=trade_volume,
                rsi=rsi,
                atr=atr,
                macd=macd
            )

            return live_data

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

    def calculate_indicators(self, candles):
        """Рассчитывает RSI, ATR, MACD на основе последних свечей"""
        df = pd.DataFrame([{
            "open": c.open.units + c.open.nano / 1e9,
            "high": c.high.units + c.high.nano / 1e9,
            "low": c.low.units + c.low.nano / 1e9,
            "close": c.close.units + c.close.nano / 1e9,
            "volume": c.volume
        } for c in candles])

        if df.empty:
            return None, None, None  # Если данных нет

        # 📌 RSI (14)
        delta = df["close"].diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
        rs = gain / loss
        df["rsi"] = 100 - (100 / (1 + rs))

        # 📌 ATR (14)
        df["tr"] = df[["high", "low", "close"]].max(axis=1) - df[["high", "low", "close"]].min(axis=1)
        df["atr"] = df["tr"].rolling(window=14).mean()

        # 📌 MACD (12, 26)
        df["ema12"] = df["close"].ewm(span=12, adjust=False).mean()
        df["ema26"] = df["close"].ewm(span=26, adjust=False).mean()
        df["macd"] = df["ema12"] - df["ema26"]

        return df["rsi"].iloc[-1], df["atr"].iloc[-1], df["macd"].iloc[-1]

    def get_trades(self, figi):
        """Получает последнюю цену и объем сделки через Streaming API"""
        trades = []

        def callback(response):
            if response.trade:
                for trade in response.trade:
                    price = trade.price.units + trade.price.nano / 1e9
                    volume = trade.quantity
                    trades.append((price, volume))
                    print(f"🔥 Сделка получена: Цена={price}, Объём={volume}")  # Логирование

        with Client(self.token) as client:
            # 🟢 Подписка на сделки (исправленный формат `instruments`)
            market_data_request = MarketDataRequest(
                subscribe_trades_request=SubscribeTradesRequest(
                    subscription_action=SubscriptionAction.SUBSCRIPTION_ACTION_SUBSCRIBE,
                    instruments=[TradeInstrument(figi=figi)],
                )
            )

            # 🟢 Запускаем подписку на поток
            client.market_data_stream.market_data_stream(
                request_iterator=[market_data_request], callback=callback
            )

            # 🟢 Улучшенное ожидание до 10 секунд
            timeout = 2  # Ждём до 10 секунд
            start_time = time.time()

            while time.time() - start_time < timeout:
                if trades:  # Если появились сделки, выходим
                    break
                time.sleep(0.5)  # Проверяем каждые 0.5 секунды

        if trades:
            return trades[-1]  # Берем последнюю сделку
        return None, None  # Если сделок не было
