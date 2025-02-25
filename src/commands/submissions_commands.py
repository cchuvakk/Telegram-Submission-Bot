from telegram import Update, constants
from telegram.ext import ContextTypes
from database.submissions_db import SubmissionsDB
from asyncio import sleep


class SubmissionsCommands:
    def __init__(self):
        self.db = SubmissionsDB()
        
    async def __checkArgs(self, args_num: int, args: list) -> bool:
        args_length = len(args)

        if(args_length > args_num or args_length <= 0):
            return False
        
        return True

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user

        if(not await self.db.userExist(user.id)):
            await self.db.createUser(user.id, user.username if user.username != None else user.first_name)

        await update.message.reply_html(rf"Привет, <b>{user.mention_html()}</b>, если у тебя есть смешное видео/картинка/гифка/голосовое, отправляй их сюда!")

    async def ban(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        message = update.effective_message

        if(not await self.__checkArgs(args_num = 1, args = context.args)):
            if(message.reply_to_message):
                banned_user = message.reply_to_message.from_user

                await update.message.reply_html(f"{banned_user.mention_html()} больше не сможет постить; Админ: {user.mention_html()}")
                await self.db.banUser(banned_user.id)

                return
            else:
                await update.message.reply_html("Использование: <b>ban [tg_userid]</b>")

                return
            
        tg_userid = context.args[0]

        if(tg_userid == None):
            return
        
        if(not await self.db.userExist(int(tg_userid))):
            return
        
        if(await self.db.userAdmin(int(tg_userid))):
            self.db.unmakeUserAdmin(int(tg_userid))
        
        if(await self.db.userBanned(int(tg_userid))):
            return
        
        await self.db.banUser(int(tg_userid))
        await update.message.reply_html(f"{tg_userid} больше не сможет постить; Админ: {user.mention_html()}")
        
    
    async def unban(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        message = update.effective_message

        if(not await self.__checkArgs(args_num = 1, args = context.args)):
            if(message.reply_to_message):
                banned_user = message.reply_to_message.from_user

                await update.message.reply_html(f"{banned_user.mention_html()} теперь может постить; Админ: {user.mention_html()}")
                await self.db.unbanUser(banned_user.id)

                return
            else:
                await update.message.reply_html("Использование: <b>unban [tg_userid]</b>")

                return

        tg_userid = context.args[0]

        if(tg_userid == None):
            return

        if(not await self.db.userExist(int(tg_userid))):
            return

        if(not await self.db.userAdmin(user.id)):
            return

        if(not await self.db.userBanned(int(tg_userid))):
            return
    
        await self.db.unbanUser(int(tg_userid))
        await update.message.reply_html(f"{tg_userid} теперь может постить; Админ: {user.mention_html()}")

    async def promoteToAdmin(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        message = update.effective_message

        if(not await self.__checkArgs(args_num = 1, args = context.args)):
            if(message.reply_to_message):
                promoted_user = message.reply_to_message.from_user

                await update.message.reply_html(f"Админ: {user.mention_html()} сделал админом: {promoted_user.mention_html()}")
                await self.db.makeUserAdmin(promoted_user.id)

                return
            else:
                await update.message.reply_html("Использование: <b>admin [tg_userid]</b>")

                return

        tg_userid = context.args[0]

        if(tg_userid == None):
            return
        
        if(not await self.db.userExist(int(tg_userid))):
            return

        if(await self.db.userAdmin(int(tg_userid))):
            return
        
        if(await self.db.userBanned(int(tg_userid))):
            return
        
        await self.db.makeUserAdmin(int(tg_userid))

        await update.message.reply_text(f"Админ: {user.mention_html()} сделал админом: {tg_userid}")
    
    async def demoteToUser(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        message = update.effective_message

        if(not await self.__checkArgs(args_num = 1, args = context.args)):
            if(message.reply_to_message):
                demoted_user = message.reply_to_message.from_user

                await update.message.reply_html(f"Админ: {user.mention_html()} убрал права админа: {demoted_user.mention_html()}")
                await self.db.unmakeUserAdmin(demoted_user.id)

                return
            else:
                await update.message.reply_html("Использование: <b>unadmin [tg_userid]</b>")

                return

        tg_userid = context.args[0]

        if(tg_userid == None):
            return
        
        if(not await self.db.userExist(int(tg_userid))):
            return

        if(not await self.db.userAdmin(int(tg_userid))):
            return
        
        await self.db.unmakeUserAdmin(int(tg_userid))

        await update.message.reply_html(f"Админ: {user.mention_html()} убрал правда админа: {tg_userid}")
