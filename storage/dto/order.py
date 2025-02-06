from dataclasses import dataclass
from datetime import datetime

@dataclass
class Order:
    figi: str
    asset_name: str
    price: float
    type: str
    timestamp: datetime
    status: str
    id: str
    linked_id: str
