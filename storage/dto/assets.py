from dataclasses import dataclass
from datetime import datetime


@dataclass
class Asset:
    figi: str  # Уникальный идентификатор инструмента
    asset_name: str  # Название актива
    price: float  # Текущая цена
    timestamp: datetime  # Время записи
