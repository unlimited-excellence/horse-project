import os

from database.database_worker import DatabaseWorker
from endpoints.telegram import TelegramBotService
from services.MiscService import MiscService
from services.UsersService import UsersService

if __name__ == '__main__':
    print("Initializing MongoDB")
    databaseWorker = DatabaseWorker(os.getenv("MONGODB_URI"), os.getenv("MONGODB_DATABASE"))

    print("Initializing MiscService")
    misc_service = MiscService(databaseWorker)
    config = misc_service.get_or_create_config()

    print("Initializing UsersService")
    users_service = UsersService(databaseWorker)

    print("Initializing Telegram Bot")
    telegram_bot_service = TelegramBotService(os.getenv("TELEGRAM_BOT_TOKEN"), users_service)

    print("Running Telegram Bot")
    telegram_bot_service.run()