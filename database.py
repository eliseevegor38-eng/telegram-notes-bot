import sqlite3
import logging
from datetime import datetime

# Настройка логирования
logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path='notes_bot.db'):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Инициализация базы данных и создание таблиц"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Таблица пользователей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Таблица заметок
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notes (
                    note_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    content TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')

            # Таблица напоминаний
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reminders (
                    reminder_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    note_id INTEGER,
                    reminder_time DATETIME,
                    is_active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (note_id) REFERENCES notes (note_id)
                )
            ''')

            conn.commit()
        logger.info("База данных инициализирована")

    def add_user(self, user_id, username, first_name):
        """Добавление пользователя в базу данных"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO users (user_id, username, first_name)
                VALUES (?, ?, ?)
            ''', (user_id, username, first_name))
            conn.commit()

    def add_note(self, user_id, content):
        """Добавление заметки для пользователя"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO notes (user_id, content)
                VALUES (?, ?)
            ''', (user_id, content))
            conn.commit()
            return cursor.lastrowid

    def get_notes(self, user_id):
        """Получение всех заметок пользователя"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT note_id, content, created_at
                FROM notes
                WHERE user_id = ?
                ORDER BY created_at DESC
            ''', (user_id,))
            return cursor.fetchall()

    def delete_note(self, user_id, note_id):
        """Удаление конкретной заметки"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM notes
                WHERE user_id = ? AND note_id = ?
            ''', (user_id, note_id))
            conn.commit()
            return cursor.rowcount

    def clear_notes(self, user_id):
        """Удаление всех заметок пользователя"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM notes
                WHERE user_id = ?
            ''', (user_id,))
            conn.commit()
            return cursor.rowcount