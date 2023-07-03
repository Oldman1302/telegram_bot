import sqlite3
import asyncio


async def db_start() -> (sqlite3, sqlite3.Cursor):
    global db, cursor
    db = sqlite3.connect("users.db")
    cursor = db.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id_user INT PRIMARY KEY, name_user TEXT)")
    print('База данных успешно синхронизирована')
    return db, cursor


# Вставляем данные в таблицу
async def create_user(user_id: int, user_name: str) -> None:
    users_data = cursor.execute(f"""SELECT 1 FROM users
                                WHERE id_user = {user_id}
                                    """).fetchone()
    if not users_data:
        cursor.execute(f"INSERT INTO users VALUES ({user_id}, '{user_name}')")
        print('Добавлен новый пользователь')
    db.commit()


# удаление таблицы
async def delete_table_users() -> None:
    # можно также использовать TRUNCATE users (работает быстрее, но триггеры срабатывать не будут)
    cursor.execute('DELETE FROM users')


async def select_all() -> None:
    print(cursor.execute('SELECT * FROM users').fetchall())


if __name__ == '__main__':
    db, cursor = asyncio.run(db_start())
    action = input(
        'Что вы хотите сделать?\n\t1. очистить Базу Данных  \n\t2. создать нового юзера \n\t3. посмотреть данные\n->')

    while True:
        if action == '1':
            asyncio.run(delete_table_users())
            break
        elif action == '2':
            asyncio.run(create_user(1, 'Kirill'))
            break
        elif action == '3':
            break
        else:
            action = input('Краказябра... Попробуй еще раз\n->')

    a = 1
    asyncio.run(select_all())
    db.commit()
