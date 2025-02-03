import pytest
from bot.tinkoff_api import TinkoffAPI

def test_get_account():
    api = TinkoffAPI()
    accounts = api.get_accounts()
    assert isinstance(accounts, list)
    assert len(accounts) > 0

def test_get_market_orderbook():
    api = TinkoffAPI()
    orderbook = api.get_orderbook(figi="BBG004730N88", depth=10)
    assert orderbook is not None
    assert orderbook.depth == 10
