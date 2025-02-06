import sqlite3 as sq
from typing import List, Tuple


class DataBaseHandler:
    def __init__(self, sqlite_database_name: str):
        self.connection = sq.connect(sqlite_database_name)
        self.connection.row_factory = sq.Row  # Enable named tuples
        self.connection.execute('''
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                title TEXT
            )
        ''')
        self.connection.commit()

    async def append(self, username: str, title: str) -> None:
        try:
            cursor = self.connection.cursor()
            cursor.execute('INSERT INTO requests (username, title) VALUES (?, ?)', (username, title))
            self.connection.commit()
        except Exception as e:
            print(f"Ошибка при добавлении запроса: {e}")


    async def user_stats(self, username: str) -> List[Tuple[str, int]]:
        try:
            cursor = self.connection.cursor()
            return cursor.execute(
                'SELECT title, COUNT(title) AS freq FROM requests WHERE username = ? GROUP BY title ORDER BY freq DESC',
                (username,)
            ).fetchall()
        except Exception as e:
            print(f"Ошибка при получении статистики: {e}")
            return []

    async def user_search_history(self, username: str) -> List[Tuple[str, ]]:
        try:
            cursor = self.connection.cursor()
            return cursor.execute(
                'SELECT title FROM requests WHERE username = ?',
                (username,)
            ).fetchall()
        except Exception as e:
            print(f"Ошибка при получении истории: {e}")
            return []

    async def close(self):
        self.connection.close()