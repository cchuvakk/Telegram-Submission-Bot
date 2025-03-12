from telegram.ext import CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram import Update
from os import getenv
from submissions import Submissions
from commands.submissions_commands import SubmissionsCommands

def main() -> None:
    bot_token = getenv("submissions_bot_token")
    bot = Submissions(bot_token)

    commands = SubmissionsCommands()
    
    adminchatid: int = -1002311508130

    media_handler = MessageHandler((filters.ChatType.PRIVATE & ~filters.COMMAND) & 
                                   (filters.PHOTO | filters.VIDEO | 
                                    filters.ANIMATION | filters.VOICE | 
                                    filters.TEXT), 
                                   bot.handleMedia)

    bot.app.add_handler(CommandHandler("start", commands.start, filters.ChatType.PRIVATE))
    bot.app.add_handler(CommandHandler("admin", commands.promoteToAdmin, filters = filters.Chat(chat_id = adminchatid)))
    bot.app.add_handler(CommandHandler("unadmin", commands.demoteToUser, filters = filters.Chat(chat_id = adminchatid)))
    bot.app.add_handler(CommandHandler("posting_ban", commands.ban, filters = filters.Chat(chat_id=adminchatid)))
    bot.app.add_handler(CommandHandler("posting_unban", commands.unban, filters = filters.Chat(chat_id = adminchatid)))
    bot.app.add_handler(media_handler)

    bot.app.add_handler(CallbackQueryHandler(bot.handleButtons))

    bot.app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()