import os
import json

CONFIG_PATH = os.getenv("CONFIG_PATH", "conf/config.json")  # Указываем путь заранее


def load_config():
    """Загружает конфигурацию сначала из переменных окружения, затем из файла JSON."""
    config = {
        "STORAGE_TYPE": os.getenv("STORAGE_TYPE"),
        "TINKOFF_API_TOKEN": os.getenv("TINKOFF_API_TOKEN"),
        "TINKOFF_SANDBOX_MODE": os.getenv("TINKOFF_SANDBOX_MODE"),
        "TRADE_MODE": os.getenv("TRADE_MODE"),
        "DATA_FOLDER": os.getenv("DATA_FOLDER"),
        "UPDATE_INTERVAL": os.getenv("UPDATE_INTERVAL"),
        "PROFIT_PERCENT": os.getenv("PROFIT_PERCENT"),
        "STOP_LOSS_PERCENT": os.getenv("STOP_LOSS_PERCENT"),
        "GRID_STEP": os.getenv("GRID_STEP"),
        "GRID_SIZE": os.getenv("GRID_SIZE"),
        "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
        "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID"),
        "ASSET_LIST": None
    }

    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as file:
            json_config = json.load(file)
            for key, value in json_config.items():
                if config[key] is None:  # Загружаем из JSON, если нет в окружении
                    config[key] = value

    if config["ASSET_LIST"] is None:
        config["ASSET_LIST"] = {
            "BBG004730N88": "Sberbank",
            "BBG000B9XRY4": "Gazprom",
            "BBG0013HGFT4": "Lukoil"
        }

    return config


class Config:
    _config = load_config()

    STORAGE_TYPE = _config["STORAGE_TYPE"] or "CSV"
    TINKOFF_API_TOKEN = _config["TINKOFF_API_TOKEN"] or ""
    TINKOFF_SANDBOX_MODE = str(_config["TINKOFF_SANDBOX_MODE"] or "False").lower() == "true"
    TRADE_MODE = (_config["TRADE_MODE"] or "TEST").upper()
    DATA_FOLDER = _config["DATA_FOLDER"] or "data"
    UPDATE_INTERVAL = int(_config["UPDATE_INTERVAL"] or 5)
    PROFIT_PERCENT = float(_config["PROFIT_PERCENT"] or 0.01)
    STOP_LOSS_PERCENT = float(_config["STOP_LOSS_PERCENT"] or 0.01)
    GRID_STEP = float(_config["GRID_STEP"] or 0.01)
    GRID_SIZE = int(_config["GRID_SIZE"] or 1)
    TELEGRAM_BOT_TOKEN = _config["TELEGRAM_BOT_TOKEN"] or ""
    TELEGRAM_CHAT_ID = _config["TELEGRAM_CHAT_ID"] or ""
    ASSET_LIST = _config["ASSET_LIST"]

    @staticmethod
    def validate():
        """Проверка обязательных параметров перед запуском"""
        if not Config.TINKOFF_API_TOKEN:
            raise ValueError("Ошибка: API-токен TINKOFF_API_TOKEN не установлен!")
        if Config.TRADE_MODE not in ["TEST", "TRADE"]:
            raise ValueError("Ошибка: Некорректный режим TRADE_MODE! Должен быть 'TEST' или 'TRADE'.")


Config.validate()
