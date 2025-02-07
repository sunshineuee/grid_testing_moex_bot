from dataclasses import dataclass
import pandas as pd
from typing import Optional, List

@dataclass
class MarketData:
    # 📊 Основные рыночные данные (Свечи)
    timestamp: pd.Timestamp
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    volume: Optional[int] = None

    # 💰 Последняя цена
    last_price: Optional[float] = None

    # 📉 Спред и ликвидность (Стакан заявок)
    bid: Optional[float] = None
    ask: Optional[float] = None
    spread: Optional[float] = None
    bid_size: Optional[int] = None
    ask_size: Optional[int] = None

    # 🔥 Поток сделок
    trade_price: Optional[float] = None
    trade_volume: Optional[int] = None

    # 📈 Индикаторы (добавляются при обработке)
    rsi: Optional[float] = None
    atr: Optional[float] = None
    macd: Optional[float] = None
