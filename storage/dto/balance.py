from dataclasses import dataclass
from datetime import datetime

@dataclass
class Balance:
    figi: str
    asset_name: str
    type: str
    timestamp: datetime
    id: str
    price: float
    account: float
    portfolio: float
