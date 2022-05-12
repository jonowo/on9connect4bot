import logging
import os
from uuid import uuid4

from dotenv import load_dotenv
from telegram import InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler, InlineQueryHandler

from constants import BLUE_EMOJI, RED_EMOJI
from game import Game

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


async def inline_query_handler(update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Play Connect 4",
            input_message_content=InputTextMessageContent(
                "Play Connect 4\n"
                "Connect 4 of your tokens in a row to win.\n"
                f"{BLUE_EMOJI}: A\n"
                f"{RED_EMOJI}: B"
            ),
            description=f"You play as {BLUE_EMOJI}"
        )
    ]
    await update.inline_query.answer(results)


async def callback_query_handler(update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
    query = update.callback_query
    data = query.data

    if data == "ignore":
        await query.answer()
        return

    game = Game.decode_from(data)


def main():
    application = ApplicationBuilder().token(os.environ["TOKEN"]).build()
    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(InlineQueryHandler(inline_query_handler))
    application.run_polling()


if __name__ == "__main__":
    main()
