# Telegram Submission Bot

Made using python-telegram-bot library and aiosqlite for async db usage


## Requirements
[Python 3.9 or Higher](https://www.python.org/downloads/)

[python-telegram-bot](https://python-telegram-bot.org/)

[sqlite3](https://www.sqlite.org/download.html)

[aiosqlite](https://github.com/omnilib/aiosqlite/tree/main)

## Usage
If you are by some reason decided to use my bot, you need to change chat and channel ids in bot's code.

Create a database in a root folder (where src folder are located) and name it **submissions.db** and type in next query:

```SQL
BEGIN TRANSACTION;

CREATE TABLE bot_users (
  tg_userid INTEGER PRIMARY KEY UNIQUE,
  tg_username TEXT NOT NULL,
  banned INTEGER DEFAULT 0,
  admin INTEGER DEFAULT 0
);

CREATE TABLE submissions (
  sumbissionid INTEGER PRIMARY KEY,
  tg_userid INTEGER NOT NULL,
  submission_type TEXT NOT NULL,
  tg_message_id INTEGER NOT NULL UNIQUE,
  file_id TEXT NOT NULL,
  sent_to_channel INTEGER DEFAULT 0, anonymous INTEGER DEFAULT 0, file_caption TEXT DEFAULT NULL,
  FOREIGN KEY(tg_userid) REFERENCES bot_users(tg_userid)
);

COMMIT;
```
After that, you can launch main.py (located in src folder)

Right now this bot has only Russian language, other may be added later.
