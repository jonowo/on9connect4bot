import logging
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)


async def cmd_start(update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hi"
    )


def main():
    application = ApplicationBuilder().token(os.environ["TOKEN"]).build()
    application.add_handler(CommandHandler("start", cmd_start))
    application.run_polling()


if __name__ == "__main__":
    main()
