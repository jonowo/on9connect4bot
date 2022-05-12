import asyncio
import logging
import os
import time
from uuid import uuid4

from dotenv import load_dotenv
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle,
                      InputTextMessageContent, Update)
from telegram.constants import ParseMode
from telegram.ext import (ApplicationBuilder, CallbackContext, CallbackQueryHandler,
                          CommandHandler, Defaults, InlineQueryHandler)

from .constants import BLUE_EMOJI, HANDSHAKE_EMOJI, RED_EMOJI, TROPHY_EMOJI
from .game import Game
from .name_store import NameStore

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

load_dotenv()
name_store = NameStore("../name_store.json")


async def cmd_start(update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hi! Start a game of Connect 4 with a friend.",
        reply_markup=InlineKeyboardMarkup.from_button(
            InlineKeyboardButton("Select chat", switch_inline_query="")
        )
    )


async def cmd_help(update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Start a game by typing my name <code>@on9connect4bot</code> in any chat.\n\n"
        "Contact my owner <a href='tg://user?id=463998526'>Jono</a> to report bugs.\n"
        "Source code: <a href='https://github.com/jonowo/on9connect4bot'>jonowo/on9connect4bot</a>"
    )


async def cmd_ping(update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
    t = time.time()
    msg = await update.message.reply_text("Pong!")
    await msg.edit_text(f"Pong! <code>{time.time() - t:.3f}s</code>")


async def inline_query_handler(update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
    name_store.set(update.effective_user.id, update.effective_user.full_name)
    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Play Connect 4",
            input_message_content=InputTextMessageContent(
                "Play Connect 4\n"
                f"{BLUE_EMOJI} {name_store.get(update.effective_user.id)}\n"
                f"{RED_EMOJI} Waiting for opponent\n"
                "Connect 4 of your tokens in a row to win."
            ),
            reply_markup=InlineKeyboardMarkup.from_button(
                InlineKeyboardButton("Join", callback_data=f"join:{update.effective_user.id}")
            ),
            description=f"You play as {BLUE_EMOJI}"
        )
    ]
    await update.inline_query.answer(results, is_personal=True)


async def callback_query_handler(update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
    query = update.callback_query
    data = query.data

    if data.startswith("join"):
        name_store.set(update.effective_user.id, update.effective_user.full_name)

        p1_id = int(data[5:])
        p2_id = update.effective_user.id
        if p1_id == p2_id:
            await query.answer("You have no friends")
            return

        game = Game.create(p1_id, p2_id)
    elif data.startswith("game"):
        game_data, _, col = data[5:].rpartition(":")
        game = Game.decode_from(game_data)

        if update.effective_user.id != game.player_ids[game.turn]:
            await query.answer("No")
            return

        try:
            game.make_move(int(col))
        except ValueError:
            await query.answer("Invalid move!")
            return
    else:
        await query.answer()
        return

    header = [
        f"{BLUE_EMOJI} {name_store.get(game.player_ids[0])}",
        f"{RED_EMOJI} {name_store.get(game.player_ids[1])}"
    ]

    res = game.check_result()
    if res == 1:
        header[game.turn] += f" {TROPHY_EMOJI}"
        reply_markup = None
    elif res == 0:
        for i in range(2):
            header[i] += f" {HANDSHAKE_EMOJI}"
        reply_markup = None
    else:
        next_turn = (game.turn + 1) % 2 if data.startswith("game") else 0
        header[next_turn] = f"> {header[next_turn]}"
        data = game.encode()

        buttons = [
            InlineKeyboardButton(str(i + 1), callback_data=f"game:{data}:{i}")
            for i in range(Game.COLS)
        ]
        reply_markup = InlineKeyboardMarkup.from_row(buttons)

    text = "\n".join([
        "Connect 4",
        *header,
        "",
        str(game)
    ])
    await asyncio.gather(
        query.answer(),
        query.edit_message_text(text=text, reply_markup=reply_markup)
    )


def main():
    application = ApplicationBuilder().token(os.environ["TOKEN"]).defaults(
        Defaults(parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    ).build()
    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("help", cmd_help))
    application.add_handler(CommandHandler("ping", cmd_ping))
    application.add_handler(InlineQueryHandler(inline_query_handler))
    application.add_handler(CallbackQueryHandler(callback_query_handler))
    application.run_polling()
    name_store.save()


if __name__ == "__main__":
    main()
