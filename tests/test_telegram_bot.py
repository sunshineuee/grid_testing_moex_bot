from bot.telegram_bot import send_telegram_message

def test_send_telegram_message():
    response = send_telegram_message("Тестовое сообщение от бота")
    assert response is True  # Если успешно отправлено
