import sqlite3

class Database:
    def __init__(self) -> None:
        self.db = 'db.db'
    
    def connect(self, query: str, *args, fetch_one: bool = False) -> any:
        """
        Выполняет запрос к базе данных.

        Параметры:
            query (str): SQL-запрос для выполнения.
            *args: Параметры для подстановки в запрос.
            fetch_one (bool): Нужно ли извлечь один результат.

        Возвращает:
            Первый столбец первой строки, если fetch_one равно True и результат существует; иначе None.
        """
        try:
            with sqlite3.connect(self.db) as conn:
                cursor = conn.cursor()
                cursor.execute(query, args)
                if fetch_one:
                    result = cursor.fetchone()
                    return result[0]
                conn.commit()
        except sqlite3.Error as e:
            print(f"Произошла ошибка: {e}")
            return None


class UserDatabase(Database):
    def __init__(self) -> None:
        super().__init__()
    
    def new_user(self, tgID, name, date_start, model):
        self.connect('''
        INSERT OR IGNORE INTO users (tgID, name, date_start, model)
        VALUES (?, ?, ?, ?)
        ''', tgID, name, date_start, model)
        print('данные сохранены')

    def change_model(self,  model, tgID):
        # Обновляем информацию о пользователе в базе данных
        self.connect('''
            UPDATE users
            SET model = ?
            WHERE tgID = ?
        ''', model, tgID)
        print('модель изменена')
    def check_status(self, tgID, description):
        status = self.connect('''
              SELECT status FROM payments
              WHERE tgID = ? AND description = ?
          ''', tgID, description, fetch_one=True)
        return status