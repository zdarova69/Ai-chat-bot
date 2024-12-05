import sqlite3

class Model:
    def __init__(self) -> None:
        self.db = 'db.db'
        self.connection = self.connect()

    def connect(self):
        try:
            return sqlite3.connect(self.db)
        except sqlite3.Error as e:
            print(f"Ошибка подключения к базе данных: {e}")
            return None
        
    def execute_query(self, query: str, *args, fetch_one: bool = False) -> any:
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
            cursor = self.connection.cursor()
            cursor.execute(query, args)
            
            if fetch_one:
                result = cursor.fetchone()
                if result is not None:
                    return result[0]
                else:
                    return None
            
            self.connection.commit()
        except Exception as e:
            print(f"An error occurred while executing the query: {e}")
            return None
 

class UserModel(Model):
    def __init__(self) -> None:
        super().__init__()

    def get_payment_id(self, tgID, description):
        model = self.execute_query('''SELECT PaymentID FROM payments 
                                   WHERE tgID = ? AND description = ?
                                   ''', tgID, description, fetch_one=True)
        return model
    def get_payment_id_by_url(self, payment_url):
        paymentID = self.execute_query('''
                                       SELECT paymentID FROM payments 
                                       WHERE payment_url = ?''', payment_url, fetch_one=True)
        return payment_url
    
    def get_model(self, tgID, column):
        
        # Формируем SQL-запрос
        query = f'''
            SELECT {column} FROM users WHERE tgID = ?
        '''
        # Выполняем запрос и возвращаем результат
        model = self.execute_query(query, tgID, fetch_one=True)
        return model
    
    def check_status(self, tgID, description):
        status = self.execute_query('''
              SELECT status FROM payments
              WHERE tgID = ? AND description = ?
          ''', tgID, description, fetch_one=True)
        return status
    
    def get_payment_url(self, tgID, description):
        payment_url = self.execute_query('''SELECT payment_url from payments 
                                               WHERE tgID = ? AND description = ?
                                               ''', tgID, description, fetch_one=True)
        return payment_url
    def get_prompt_by_payment_id(self, paymentID):
        """
        Получает prompt из таблицы images, зная paymentID.

        :param paymentID: Идентификатор платежа, для которого нужно получить prompt.
        :return: Значение prompt или None, если запись не найдена.
        """
        result = self.execute_query('''
                                    SELECT prompt
                                    FROM images
                                    WHERE paymentID = ?
                                    ''', paymentID, fetch_one=True)
        return result
    def check_payment_exist(self,tgID, description):
        payment_url = self.execute_query('''SELECT * from payments 
                                               WHERE tgID = ? AND description = ?
                                               ''', tgID, description, fetch_one=True)
        return payment_url
    def update_payment(self, PaymentID, status, value, created_at, payment_url, tgID, description):
        self.execute_query('''
                           UPDATE payments
                        SET PaymentID = ?, status = ?, value = ?, created_at = ?, payment_url =?
                        WHERE tgID = ? AND description = ?
                    ''', PaymentID, status, value, created_at, payment_url, tgID, description)
        print('запись изменена')
    def update_payment_status(self,status ,PaymentID):
        self.execute_query('''
                           UPDATE payments
                        SET status = ? 
                        WHERE PaymentID = ?
                    ''', status ,PaymentID)
        print('запись изменена')

    def change_model(self,column,  model, tgID):
        # Обновляем информацию о пользователе в базе данных
        self.execute_query(f'''
        UPDATE users
        SET {column} = ?
        WHERE tgID = ?
    ''', model, tgID)
        print('модель изменена')
    def update_image_url(self, paymentID, new_image_url):
        """
        Обновляет image_url в таблице images, где paymentID соответствует заданному значению.

        :param paymentID: Идентификатор платежа, для которого нужно обновить image_url.
        :param new_image_url: Новое значение для image_url.
        """
        self.execute_query('''
                        UPDATE images
                        SET image_url = ?
                        WHERE paymentID = ?
                        ''', new_image_url, paymentID)
        print(f"Обновлен image_url для paymentID: {paymentID}")
    def new_user(self, tgID, name, date_start, model, imageModel):
        self.execute_query('''
        INSERT OR IGNORE INTO users (tgID, name, date_start, model, imageModel)
        VALUES (?, ?, ?, ?)
        ''', tgID, name, date_start, model, imageModel)
        print('данные сохранены')

    def add_payment(self, PaymentID, status, description, tgID, value, created_at, payment_url):
        self.execute_query('''
                        INSERT INTO payments (PaymentID, status, description, tgID, value, created_at, payment_url)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', PaymentID, status, description, tgID, value, created_at, payment_url)
        print('запись добавлена')
    def add_subscriptions(self, type, tgID, paymentID):
        self.execute_query('''
                           INSERT into subscriptions (type, tgID, paymentID) 
                           VALUES (?, ?, ?)
                           ''',type, tgID, paymentID)
    def add_image(self, tgID, paymentID, prompt):
        self.execute_query('''
                           INSERT into images (tgID, paymentID, prompt) 
                           VALUES (?, ?, ?)
                           ''',tgID, paymentID,prompt)