import os

class Config:
    # Загружаем токен и режим из переменных окружения
    TINKOFF_API_TOKEN = os.getenv("TINKOFF_API_TOKEN", "")
    TINKOFF_SANDBOX_MODE = os.getenv("TINKOFF_SANDBOX_MODE", "False").lower() == "true"

    # Настройки для торговли
    TRADE_MODE = os.getenv("TRADE_MODE", "TEST").upper()  # TEST или TRADE
    DATA_FOLDER = os.getenv("DATA_FOLDER", "data")  # Папка для хранения CSV-файлов
    UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", 5))  # Интервал обновления данных (в секундах)
    PROFIT_PERCENT = 1.0  # Процент прибыли для закрытия сделки
    STOP_LOSS_PERCENT = 1.0  # Процент убытка для закрытия сделки

    # Настройки Telegram (если нужна интеграция)
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

    GRID_STEP = 2  # Шаг сетки в процентах
    GRID_SIZE = 5  # Количество ордеров вверх и вниз от текущей цены

    @staticmethod
    def validate():
        """Проверка обязательных параметров перед запуском"""
        if not Config.TINKOFF_API_TOKEN:
            raise ValueError("Ошибка: API-токен TINKOFF_API_TOKEN не установлен!")
        if Config.TRADE_MODE not in ["TEST", "TRADE"]:
            raise ValueError("Ошибка: Некорректный режим TRADE_MODE! Должен быть 'TEST' или 'TRADE'.")

# Проверяем конфиг перед запуском
Config.validate()
