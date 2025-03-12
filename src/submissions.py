from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, constants
from telegram.ext import Application, ContextTypes
from asyncio import sleep
from database.submissions_db import SubmissionsDB

class Submissions:
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.__admin_chatid = "-1002311508130"
        self.__channelid = "-1002158915074"
        self.app = Application.builder().token(bot_token).build()
        self.db = SubmissionsDB()
    
    async def handleMediaChecks(self, update: Update) -> tuple:
        message_type = None
        
        if(update.message.photo):
            file_id = update.message.photo[-1].file_id
            message_type = "Photo"
        elif(update.message.video):
            file_id = update.message.video.file_id
            message_type = "Video"
        elif(update.message.animation):
            file_id = update.message.animation.file_id
            message_type = "Animation"
        elif(update.message.voice):
            file_id = update.message.voice.file_id
            message_type = "Voice Message"
        elif(update.message.text):
            file_id = update.message.text
            message_type = "Text"

        return file_id, message_type
        

    async def handleMedia(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user

        user_id = update.message.from_user.id

        if(not await self.db.userExist(user.id)):
            await self.db.createUser(user.id, user.username if user.username != None else user.first_name)

        if(await self.db.userBanned(user_id)):
            return
        
        message_id = update.message.id
        message_type = None

        file_id, message_type = await self.handleMediaChecks(update)

        if(update.message.caption):
            caption = update.message.caption
        else:
            caption = None

        submission_id = await self.db.insertSubmission(user_id, message_type, file_id, message_id, 0, caption)

        anonimity_keyboard = [
            [InlineKeyboardButton(text = "✅ Да", callback_data=f"anon:{submission_id}")],
            [InlineKeyboardButton(text = "❌ Нет", callback_data=f"public:{submission_id}")]
        ]

        anonymous_reply_markup = InlineKeyboardMarkup(anonimity_keyboard)

        await context.bot.send_message(chat_id = user_id, 
            text = "Анонимный пост?", 
            reply_markup=anonymous_reply_markup)
            

    async def sendSubmissionToChannel(self, username: str, messagetype: str, 
                                      anonymous: bool, file_id: str, 
                                      file_caption: str, context: ContextTypes.DEFAULT_TYPE) -> None:
        caption = f'Отправлено {username}'

        if(anonymous):
            caption = f'Отправлено анонимно'

        #dont blame me
        full_caption = str(caption) + str(file_caption)

        if(messagetype == "Photo"):
            await context.bot.send_photo(self.__channelid, photo = file_id, caption=full_caption)
        elif(messagetype == "Video"):
            await context.bot.send_video(self.__channelid, video = file_id, caption=full_caption)  
        elif(messagetype == "Animation"):
            await context.bot.send_animation(self.__channelid, animation = file_id, caption=full_caption)
        elif(messagetype == "Voice Message"):
            await context.bot.send_voice(self.__channelid, voice = file_id, caption = full_caption)
        elif(messagetype == "Text"):
            await context.bot.send_message(self.__channelid, text = file_id + '\n\n' + caption)

    async def handleButtons(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()

        action, submissionid = query.data.split(":")
        submissionid = int(submissionid)
        admin_id = query.from_user.id

        submission = await self.db.getSubmissionData(submissionid)

        if not submission:
            return

        tg_userid, submission_type, tg_message_id, file_id, anonymous, db_file_caption = submission[0], submission[1], submission[2], submission[3], submission[4], submission[5]

        db_file_caption = f'\n\nКомментарий:  {db_file_caption}' if db_file_caption != None else '\n'

        username = await self.db.getUsername(tg_userid)

        if(action in ["anon", "public"]):
            if(action == "anon"):
                await self.db.setAnonymous(submissionid)

            await query.delete_message()

            keyboard = [
                [InlineKeyboardButton(text = "✅ Запостить", callback_data=f"post:{submissionid}")],
                [InlineKeyboardButton(text = "❌ Не постить", callback_data=f"refuse:{submissionid}")],
                [InlineKeyboardButton(text = "🔒 Забанить пользователя", callback_data=f"ban:{submissionid}")]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)

            if(submission_type == "Photo"):
                await context.bot.send_photo(chat_id = self.__admin_chatid, 
                                             photo = file_id, caption = f"Фотку прислал @{username} {db_file_caption}", 
                                             reply_markup = reply_markup)
            elif(submission_type == "Video"):
                await context.bot.send_video(chat_id = self.__admin_chatid, 
                                             video= file_id, 
                                             caption = f"Видео прислал @{username} {db_file_caption}", 
                                             reply_markup = reply_markup)
            elif(submission_type == "Animation"):
                await context.bot.send_animation(chat_id = self.__admin_chatid, 
                                                 animation = file_id, caption = f"Файлик прислал @{username} {db_file_caption}", 
                                                 reply_markup = reply_markup)
            elif(submission_type == "Voice Message"):
                await context.bot.send_voice(chat_id = self.__admin_chatid, 
                                             voice = file_id, 
                                             caption = f"Голосовое прислал @{username} {db_file_caption}", 
                                             reply_markup = reply_markup)
            elif(submission_type == "Text"):
                await context.bot.send_message(chat_id = self.__admin_chatid, 
                                               text = file_id + f"\n\nТекст прислал @{username}", 
                                               reply_markup = reply_markup)

        elif(action == "post"):
            if(not await self.db.userAdmin(query.from_user.id)):
                await query.answer("Вы не администратор!")
                return

            if(submission_type == "Photo" or submission_type == "Video" or submission_type == "Animation" or submission_type == "Voice Message"):
                await query.edit_message_caption(f"Выложено на канал; Админ: @{await self.db.getUsername(admin_id)}")
            else:
                await query.edit_message_text(f"Выложено на канал; Админ: @{await self.db.getUsername(admin_id)}")

            await context.bot.set_message_reaction(tg_userid, tg_message_id, constants.ReactionEmoji.RED_HEART)

            await self.db.changeSubmissionStatus(submissionid)

            await self.sendSubmissionToChannel(username, submission_type, anonymous, file_id, db_file_caption, context)

            await sleep(2)

            await query.delete_message()

        elif(action == "refuse"):
            if(not await self.db.userAdmin(query.from_user.id)):
                await query.answer("Вы не администратор!")
                return

            if(submission_type == "Photo" or submission_type == "Video" or submission_type == "Animation" or submission_type == "Voice Message"):
                await query.edit_message_caption(f"Не будет выложено; Админ: @{await self.db.getUsername(admin_id)}")
            else:  
                await query.edit_message_text(f"Не будет выложено; Админ: @{await self.db.getUsername(admin_id)}")

            await context.bot.set_message_reaction(tg_userid, tg_message_id, constants.ReactionEmoji.THUMBS_DOWN)

            await sleep(2)

            await query.delete_message()

        elif(action == "ban"):
            if(not await self.db.userAdmin(query.from_user.id)):
                await query.answer("Вы не администратор!")
                return

            if(await self.db.userAdmin(tg_userid)):
                await self.db.unmakeUserAdmin(tg_userid)
            
            if(submission_type == "Photo" or submission_type == "Video" or submission_type == "Animation" or submission_type == "Voice Message"):
                await query.edit_message_caption(f"Забанен нахер уродец; Админ: @{await self.db.getUsername(admin_id)}")
            else:
                await query.edit_message_text(f"Забанен нахер уродец; Админ: @{await self.db.getUsername(admin_id)}")

            await context.bot.set_message_reaction(tg_userid, tg_message_id, constants.ReactionEmoji.REVERSED_HAND_WITH_MIDDLE_FINGER_EXTENDED)

            await self.db.banUser(tg_userid)

            await sleep(2)

            await query.delete_message()

    

