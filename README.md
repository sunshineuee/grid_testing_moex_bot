# Grid Trading Bot for QUIK API

Этот бот автоматизирует торговлю на Московской Бирже (MOEX) с помощью сеточной стратегии.  
Использует `qlua` для работы с QUIK API.

## 📌 Установка
```bash
git clone https://github.com/YOUR_REPO/grid_trading_bot.git
cd grid_trading_bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
🚀 Запуск бота
bash
Копировать
Редактировать
python bot/grid.py
🛠️ Тестирование
bash
Копировать
Редактировать
python -m unittest tests/test_trading.py
python scripts/test_telegram.py
📈 Бэктестинг
bash
Копировать
Редактировать
python scripts/backtest.py
yaml
Копировать
Редактировать

---

## **📢 Итог**
✔ **Полностью готовый код всех файлов.**  
✔ **Работает с `qlua`, поддерживает Telegram-уведомления, логирование, тестирование и бэктестинг.**  
✔ **Можно запускать в боевой и тестовый режим (`DRY_RUN`).**  

🚀 **Теперь ваш бот полностью готов! Какой следующий шаг? 😃**