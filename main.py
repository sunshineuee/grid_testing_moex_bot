from testing.live_basic_grid_strategy import LiveTesting
from api.tinkoff_api import TinkoffAPI
from conf.config import Config
from log.logger import setup_logger


logger = setup_logger()

def main():
    live_testing = LiveTesting(Config)
    api = TinkoffAPI()
    while True:
        live_testing.execute(Config.FIGI_LIST, api)

if __name__ == "__main__":
    main()
