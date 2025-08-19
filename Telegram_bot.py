from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Замените 'YOUR_TOKEN' на токен вашего бота
BOT_TOKEN = '8262969903:AAECcIZiN5oz0RXa9kYqo8D_1YYWFvW_39g'


# Обработчик команды /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Привет! Я бот. Как дела?')


# Обработчик команды /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Я простой бот. Отправь мне сообщение, и я отвечу!')


# Обработчик текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if 'привет' in text:
        await update.message.reply_text('Привет!')
    elif 'как дела' in text:
        await update.message.reply_text('Отлично! А у тебя?')
    else:
        await update.message.reply_text('Не понимаю, попробуй еще раз')


# Обработчик ошибок
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Ошибка: {context.error}')


# Основная функция
def main():
    # Создаем приложение
    app = Application.builder().token(BOT_TOKEN).build()

    # Добавляем обработчики
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Добавляем обработчик ошибок
    app.add_error_handler(error_handler)

    # Запускаем бота
    print('Бот запущен...')
    app.run_polling(poll_interval=3)


if __name__ == '__main__':
    main()