import aiosqlite

class SubmissionsDB:
    def __init__(self):
        self.__dbname = 'submissions.db'

    async def createUser(self, tg_userid: int, tg_username: str) -> None:
        async with aiosqlite.connect(self.__dbname) as db:
            query = 'INSERT INTO bot_users (tg_userid, tg_username) VALUES (?, ?)'
            cursor = await db.cursor()

            await cursor.execute(query, (tg_userid, tg_username))
            await db.commit()
    
    async def banUser(self, tg_userid: int) -> None:
        async with aiosqlite.connect(self.__dbname) as db:
            query = 'UPDATE bot_users SET banned = 1 WHERE tg_userid = ?'
            cursor = await db.cursor()

            await cursor.execute(query, (tg_userid,))
            await db.commit()
    
    async def unbanUser(self, tg_userid: int) -> None:
        async with aiosqlite.connect(self.__dbname) as db:
            query = 'UPDATE bot_users SET banned = 0 WHERE tg_userid = ?'
            cursor = await db.cursor()

            await cursor.execute(query, (tg_userid,))
            await db.commit()

    async def userExist(self, tg_userid: int) -> bool:
        async with aiosqlite.connect(self.__dbname) as db:
            query = 'SELECT 1 FROM bot_users WHERE tg_userid = ?'
            cursor = await db.cursor()

            await cursor.execute(query, (tg_userid,))

            result = await cursor.fetchone()

            if(result == None):
                return 0
            
            return result[0]
        
    async def userAdmin(self, tg_userid: int) -> bool:
        async with aiosqlite.connect(self.__dbname) as db:
            query = 'SELECT admin FROM bot_users WHERE tg_userid = ?'
            cursor = await db.cursor()

            await cursor.execute(query, (tg_userid,))

            result = await cursor.fetchone()

            if(result == None):
                return 0
            
        return result[0]
    
    async def makeUserAdmin(self, tg_userid: int) -> None:
        async with aiosqlite.connect(self.__dbname) as db:
            query = 'UPDATE bot_users SET admin = 1 WHERE tg_userid = ?'
            cursor = await db.cursor()

            await cursor.execute(query, (tg_userid,))

            await db.commit()
    
    async def unmakeUserAdmin(self, tg_userid: int) -> None:
        async with aiosqlite.connect(self.__dbname) as db:
            query = 'UPDATE bot_users SET admin = 0 WHERE tg_userid = ?'
            cursor = await db.cursor()

            await cursor.execute(query, (tg_userid,))

            await db.commit()

    async def getUsername(self, tg_userid: int) -> str:
        async with aiosqlite.connect(self.__dbname) as db:
            query = 'SELECT tg_username FROM bot_users WHERE tg_userid = ?'
            cursor = await db.cursor()

            await cursor.execute(query, (tg_userid,))

            result = await cursor.fetchone()

            if(result == None):
                return 0
            
        return result[0]

    async def userBanned(self, tg_userid: int) -> bool:
        async with aiosqlite.connect(self.__dbname) as db:
            query = 'SELECT banned FROM bot_users WHERE tg_userid = ?'
            cursor = await db.cursor()

            await cursor.execute(query, (tg_userid,))

            result = await cursor.fetchone()

            if(result == None):
                return 0
            
        return result[0]
    
    async def getSubmissionData(self, submissionid: int) -> tuple:
        async with aiosqlite.connect(self.__dbname) as db:
            query = 'SELECT tg_userid, submission_type, tg_message_id, file_id, anonymous, file_caption FROM submissions WHERE sumbissionid = ?'
            cursor = await db.cursor()

            await cursor.execute(query, (submissionid,))

            result = await cursor.fetchone()

            if(result == None):
                return 0
            
            return result
        
        
    async def insertSubmission(self, tg_userid: int, submission_type: str, file_id: str, tg_message_id: str, anonymous_submission: int, file_caption: str) -> int:
        async with aiosqlite.connect(self.__dbname) as db:
            query = 'INSERT INTO submissions (tg_userid, submission_type, tg_message_id, file_id, sent_to_channel, anonymous, file_caption) values (?, ?, ?, ?, ?, ?, ?)'
            cursor = await db.cursor()

            await cursor.execute(query, (tg_userid, submission_type, tg_message_id, file_id, 0, anonymous_submission, file_caption))

            await db.commit()
        return cursor.lastrowid
    
    async def deleteSubmission(self, submission_id: int) -> None:
        async with aiosqlite.connect(self.__dbname) as db:
            query = 'DELET FROM submissions where sumbissionid = ?'
            cursor = await db.cursor()

            await cursor.execute(query, (submission_id,))

            await db.commit()

    async def changeSubmissionStatus(self, submission_id: str) -> None:
        async with aiosqlite.connect(self.__dbname) as db:
            query = 'UPDATE submissions SET sent_to_channel = 1 WHERE sumbissionid = ?'
            cursor = await db.cursor()

            await cursor.execute(query, (submission_id,))

            await db.commit()

    async def setAnonymous(self, submission_id: str) -> None:
        async with aiosqlite.connect(self.__dbname) as db:
            query = 'UPDATE submissions SET anonymous = 1 WHERE sumbissionid = ?'
            cursor = await db.cursor()

            await cursor.execute(query, (submission_id,))

            await db.commit()