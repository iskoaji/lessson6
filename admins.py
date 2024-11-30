import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from config import token


bot = Bot(token=token)
dp = Dispatcher()


conn = sqlite3.connect("bot_database.db", check_same_thread=False)
cursor = conn.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    chat_id INTEGER,
    is_admin BOOLEAN DEFAULT FALSE
)
""")
conn.commit()



@dp.message(Command("start"))
async def start_command(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    chat_id = message.chat.id

    
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    if cursor.fetchone() is None:
        cursor.execute("""
        INSERT INTO users (user_id, username, chat_id) VALUES (?, ?, ?)
        """, (user_id, username, chat_id))
        conn.commit()
        await message.answer("Вы зарегистрированы в боте.")
    else:
        await message.answer("Вы уже зарегистрированы.")
    await message.answer("Добро пожаловать в бот!")



@dp.message(Command("mailing"))
async def mailing_command(message: types.Message):
    cursor.execute("SELECT is_admin FROM users WHERE user_id = ?", (message.from_user.id,))
    is_admin = cursor.fetchone()
    if not is_admin or not is_admin[0]:
        await message.answer("У вас нет прав для этой команды.")
        return

    
    cursor.execute("SELECT chat_id FROM users")
    users = cursor.fetchall()

    for user in users:
        try:
            await bot.send_message(user[0], "Это рассылка от админа!")
        except Exception:
            continue

    await message.answer("Рассылка завершена.")


@dp.message(Command("users"))
async def users_command(message: types.Message):
    cursor.execute("SELECT is_admin FROM users WHERE user_id = ?", (message.from_user.id,))
    is_admin = cursor.fetchone()
    if not is_admin or not is_admin[0]:
        await message.answer("У вас нет прав для этой команды.")
        return

    cursor.execute("SELECT username, user_id FROM users")
    users = cursor.fetchall()
    user_list = "\n".join([f"@{user[0]} (ID: {user[1]})" for user in users])
    await message.answer(f"Список пользователей:\n{user_list}")



@dp.message(Command("add_admin"))
async def add_admin_command(message: types.Message):
    cursor.execute("SELECT is_admin FROM users WHERE user_id = ?", (message.from_user.id,))
    is_admin = cursor.fetchone()
    if not is_admin or not is_admin[0]:
        await message.answer("У вас нет прав для этой команды.")
        return

    await message.answer("Введите ID пользователя, которого хотите сделать админом:")
    user_id = message.text.strip()

    try:
        cursor.execute("UPDATE users SET is_admin = TRUE WHERE user_id = ?", (user_id,))
        conn.commit()
        await message.answer(f"Пользователь с ID {user_id} стал админом.")
    except Exception as e:
        await message.answer("Ошибка")



async def main():
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
