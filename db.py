import pymysql
import json

class Model:
    def __init__(self) -> None:
        self.db = {
            'database': 'mydb',  # Имя базы данных
            'user': 'root',      # Имя пользователя
            'password': '12345', # Пароль
            'host': 'localhost', # IP-адрес или доменное имя сервера
            'port': 3306         # Порт (по умолчанию 3306 для MySQL)
        }
        self.connection = self.connect()

    def connect(self):
        try:
            connection = pymysql.connect(**self.db)
            print("Соединение с базой данных установлено.")
            return connection
        except pymysql.MySQLError as e:
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
            with self.connection.cursor() as cursor:
                cursor.execute(query, args)
                
                if fetch_one:
                    result = cursor.fetchone()
                    if result is not None:
                        return result[0]
                    else:
                        return None
                
                self.connection.commit()
        except pymysql.MySQLError as e:
            print(f"Ошибка выполнения запроса: {e}")
            return None

    def close(self):
        """
        Закрывает соединение с базой данных.
        """
        if self.connection:
            self.connection.close()
            print("Соединение с базой данных закрыто.")
            
class UserModel(Model):
    def __init__(self) -> None:
        super().__init__()

    def get_payment_id(self, tgID, description):
        """
        Получает PaymentID из таблицы payments по tgID и description.
        """
        query = '''
            SELECT paymentID FROM payments 
            WHERE tgID = %s AND description = %s
        '''
        return self.execute_query(query, tgID, description, fetch_one=True)

    def get_payment_id_by_url(self, payment_url):
        """
        Получает PaymentID из таблицы payments по payment_url.
        """
        query = '''
            SELECT paymentID FROM payments 
            WHERE payment_url = %s
        '''
        return self.execute_query(query, payment_url, fetch_one=True)

    def get_model(self, tgID, column):
        """
        Получает значение указанного столбца из таблицы users по tgID.
        """
        query = f'''
            SELECT {column} FROM users WHERE tgID = %s
        '''
        return self.execute_query(query, tgID, fetch_one=True)

    def check_status(self, tgID, description):
        """
        Получает статус из таблицы payments по tgID и description.
        """
        query = '''
            SELECT status FROM payments
            WHERE tgID = %s AND description = %s
        '''
        return self.execute_query(query, tgID, description, fetch_one=True)

    def get_payment_url(self, tgID, description):
        """
        Получает payment_url из таблицы payments по tgID и description.
        """
        query = '''
            SELECT payment_url FROM payments 
            WHERE tgID = %s AND description = %s
        '''
        return self.execute_query(query, tgID, description, fetch_one=True)

    def get_prompt_by_payment_id(self, paymentID):
        """
        Получает prompt из таблицы images по paymentID.
        """
        query = '''
            SELECT prompt
            FROM images
            WHERE paymentID = %s
        '''
        return self.execute_query(query, paymentID, fetch_one=True)

    def check_payment_exist(self, tgID, description):
        """
        Проверяет, существует ли запись в таблице payments по tgID и description.
        """
        query = '''
            SELECT * FROM payments 
            WHERE tgID = %s AND description = %s
        '''
        return self.execute_query(query, tgID, description, fetch_one=True)
    
    def check_user_subscription(self, tgID):
        """
        Проверяет, существует ли запись в таблице subscriptions по tgID
        """
        query = '''
            SELECT * FROM subscriptions 
            WHERE tgID = %s 
        '''
        return self.execute_query(query, tgID, fetch_one=True)
    
    def select_messages(self, tgID):
        query = """
            SELECT messages 
            FROM users
            WHERE tgID = %s
        """
        messages = self.execute_query(query, tgID, fetch_one=True)
        messages_dict = json.loads(messages)
        return messages_dict
        
    def update_context_clear(self, tgID):
        query = '''
            UPDATE users
            SET messages = '[{"role": "system", "content": "ты - чат-бот ассистент."}]'
            WHERE tgID = %s;
        '''
        self.execute_query(query, tgID)

    def update_payment(self, PaymentID, status, value, created_at, expires_at, payment_url, tgID, description):
        """
        Обновляет запись в таблице payments.
        """
        query = '''
            UPDATE payments
            SET paymentID = %s, status = %s, value = %s, created_at = %s, expires_at = %s, payment_url = %s
            WHERE tgID = %s AND description = %s
        '''
        self.execute_query(query, PaymentID, status, value, created_at, expires_at, payment_url, tgID, description)
        print('Запись изменена')

    def update_payment_status(self, status, PaymentID):
        """
        Обновляет статус платежа в таблице payments по PaymentID.
        """
        query = '''
            UPDATE payments
            SET status = %s 
            WHERE paymentID = %s
        '''
        self.execute_query(query, status, PaymentID)
        print('Запись изменена')

    def change_model(self, column, model, tgID):
        """
        Обновляет указанный столбец в таблице users по tgID.
        """
        query = f'''
            UPDATE users
            SET {column} = %s
            WHERE tgID = %s
        '''
        self.execute_query(query, model, tgID)
        print('Модель изменена')

    def update_image_url(self, paymentID, new_image_url):
        """
        Обновляет image_url в таблице images по paymentID.
        """
        query = '''
            UPDATE images
            SET image_url = %s
            WHERE paymentID = %s
        '''
        self.execute_query(query, new_image_url, paymentID)
        print(f"Обновлен image_url для paymentID: {paymentID}")
    def update_messages(self, tgID, messages):
        json_messages = json.dumps(messages)
        query = """
            UPDATE users
            SET messages = %s
            WHERE tgID = %s
        """
        self.execute_query(query, json_messages, tgID)
    def new_user(self, tgID, name, date_start, model, imageModel):
        """
        Добавляет нового пользователя в таблицу users.
        """
        query = '''
            INSERT INTO users (tgID, name, date_start, model, imageModel)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE tgID = tgID
        '''
        self.execute_query(query, tgID, name, date_start, model, imageModel)
        print('Данные сохранены')

    def add_payment(self, PaymentID, status, description, tgID, value, created_at, expires_at, payment_url):
        """
        Добавляет новую запись в таблицу payments.
        """
        query = '''
            INSERT INTO payments (paymentID, status, description, tgID, value, created_at, expires_at, payment_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        '''
        self.execute_query(query, PaymentID, status, description, tgID, value, created_at, expires_at, payment_url)
        print('Запись добавлена')

    def add_subscriptions(self, type, tgID, paymentID):
        """
        Добавляет новую запись в таблицу subscriptions.
        """
        query = '''
            INSERT INTO subscriptions (type, tgID, paymentID) 
            VALUES (%s, %s, %s)
        '''
        self.execute_query(query, type, tgID, paymentID)

    def add_image(self, tgID, paymentID, prompt):
        """
        Добавляет новую запись в таблицу images.
        """
        query = '''
            INSERT INTO images (tgID, paymentID, prompt) 
            VALUES (%s, %s, %s)
        '''
        self.execute_query(query, tgID, paymentID, prompt)