from testing.live_basic_grid_strategy import LiveTesting
from api.tinkoff_api import TinkoffAPI
from conf.config import Config
from log.logger import setup_logger


logger = setup_logger()

def main():
    live_testing = LiveTesting(Config)
    api = TinkoffAPI()
    while True:
        for figi, asset_name in Config.FIGI_LIST.items():
            price = api.get_current_price(figi)
            live_testing.execute(figi, asset_name, price)

if __name__ == "__main__":
    main()
