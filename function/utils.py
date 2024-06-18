import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
import string
import pymysql
import time
from xpinyin import Pinyin

def send_registration_email(user_email, auth_code):
    try:
        sender_email = '' 
        sender_password = ''
        subject = '注册成功确认' 
        message = f'你好，\n\n感谢你注册我们的聊天室。你的账户已成功创建。\n\n你的授权码是：{auth_code}\n注：请牢记授权码，这将是您找回密码的重要凭证。\n\n祝你使用愉快! 😊\n\n聊天室团队'

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = user_email
        msg['Subject'] = subject

        msg.attach(MIMEText(message, 'plain', 'utf-8'))

        smtp_server = 'smtp.qq.com' 
        smtp_port = 587 

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()

        server.login(sender_email, sender_password)

        server.sendmail(sender_email, user_email, msg.as_string())

        server.quit()

        print('Email send success')
    except Exception as e:
        print('Email send fail:', str(e))

def send_password_email(user_email, password):
    try:
        sender_email = '' 
        sender_password = ''
        subject = '密码找回' 
        message = f'你好，\n\n你的密码是：{password}\n注：请妥善保管你的密码。\n\n祝你使用愉快! 😊\n\n聊天室团队'

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = user_email
        msg['Subject'] = subject

        msg.attach(MIMEText(message, 'plain', 'utf-8'))

        smtp_server = 'smtp.qq.com' 
        smtp_port = 587 

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()

        server.login(sender_email, sender_password)

        server.sendmail(sender_email, user_email, msg.as_string())

        server.quit()

        print('Email send success')
    except Exception as e:
        print('Email send fail:', str(e))

def generate_auth_code():
    digits = ''.join(random.choices(string.digits, k=4))
    letters = ''.join(random.choices(string.ascii_uppercase, k=2))
    auth_code = ''.join(random.sample(digits + letters, k=6))
    
    return auth_code

def contains_chinese(s):
    for char in s:
        if '\u4e00' <= char <= '\u9fff':
            return True
    return False

def conversion_table_name(room_name):
    p = Pinyin()
 
    if contains_chinese(room_name):
     
        return p.get_pinyin(room_name, '')
    else:
        return room_name
#------------------- MySQL -------------------
class Database:
    def __init__(self, host='', port=3306, user='root', passwd='', charset='utf8', db=None):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.charset = charset
        self.db = db

    def connect(self):
        return pymysql.connect(host=self.host,
                               port=self.port,
                               user=self.user,
                               passwd=self.passwd,
                               charset=self.charset,
                               db=self.db)

    def execute_query(self, query, *args):
        try:
            with self.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, args)
                    return cursor.fetchall()
        except pymysql.Error as e:
            print(f"Error executing query: {e}")
            return None

class DataProcessing:
    def __init__(self, database):
        self.db = database

    def create_table(self, table_name, columns):
        """
        创建表格

        Args:
        - table_name: 表格名称
        - columns: 包含列名和数据类型的列表，例如 [('column1', 'INT'), ('column2', 'VARCHAR(255)')]

        Returns:
        - 无
        """
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    create_query = f"CREATE TABLE IF NOT EXISTS {table_name} ("
                    for column in columns:
                        create_query += f"{column[0]} {column[1]}, "
                    create_query = create_query[:-2] + ") DEFAULT CHARSET=utf8"

                    cursor.execute(create_query)
                    conn.commit()
                    print(f"Table '{table_name}' created successfully.")
        except pymysql.Error as e:
            print(f"Error creating table: {e}")

    def drop_table(self, table_name):
        """
        删除表格

        Args:
        - table_name: 表格名称

        Returns:
        - 无
        """
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    drop_query = f"DROP TABLE IF EXISTS {table_name}"
                    cursor.execute(drop_query)
                    conn.commit()
                    print(f"Table '{table_name}' dropped successfully.")
                    return True
        except pymysql.Error as e:
            print(f"Error dropping table: {e}")
            return False

    def insert_data(self, table_name, columns, values):
        """
        插入数据

        Args:
        - table_name: 表格名称
        - columns: 列名列表，例如 ['column1', 'column2']
        - values: 值列表，例如 [value1, value2]

        Returns:
        - 无
        """
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['%s']*len(columns))})"
                    cursor.execute(insert_query, values)
                    conn.commit()
                    print(f"Data inserted into table '{table_name}' successfully.")
        except pymysql.Error as e:
            print(f"Error inserting data: {e}")

    def update_table(self, table_name, name, column_name, new_value):
        """
        更新表格中的数据

        Args:
        - table_name: 表格名称
        - name: 条件字段的值
        - column_name: 要更新的列名
        - new_value: 新的值

        Returns:
        - 无
        """
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    update_query = f"UPDATE {table_name} SET {column_name} = %s WHERE name = %s"
                    cursor.execute(update_query, (new_value, name))
                    conn.commit()
                    print(f"Value in column '{column_name}' updated successfully for '{name}'.")
        except pymysql.Error as e:
            print(f"Error updating table: {e}")

    def query_table(self, table_name, column_name, value):
        """
        查询表格中的数据

        Args:
        - table_name: 表格名称
        - column_name: 条件字段的列名
        - value: 条件字段的值

        Returns:
        - 无
        """
        try:
            query = f"SELECT * FROM {table_name} WHERE {column_name} = %s"
            rows = self.db.execute_query(query, value)
            if rows:
                #print(f"Query results for {column_name} = {value}:")
                return rows
            else:
                print(f"No rows found where {column_name} = {value}.")
        except pymysql.Error as e:
            print(f"Error querying table: {e}")

    def modify_table(self, table_name, action, column_name, column_type):
        """
        修改表格结构

        Args:
        - table_name: 表格名称
        - action: 'add' 表示添加列，'delete' 表示删除列
        - column_name: 列名
        - column_type: 列类型

        Returns:
        - 无
        """
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    if action == "add":
                        cursor.execute(f"SHOW COLUMNS FROM {table_name} LIKE '{column_name}'")
                        if cursor.fetchone():
                            print(f"Column '{column_name}' already exists in table '{table_name}'.")
                            return
                        
                        alter_query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
                    elif action == "delete":
                        alter_query = f"ALTER TABLE {table_name} DROP COLUMN {column_name}"

                    cursor.execute(alter_query)
                    conn.commit()
                    print(f"Table '{table_name}' modified successfully.")
        except pymysql.Error as e:
            print(f"Error modifying table: {e}")

    def delete_row(self, table_name, column_name, value):
        """
        删除表格中的行

        Args:
        - table_name: 表格名称
        - column_name: 条件字段的列名
        - value: 条件字段的值

        Returns:
        - 无
        """
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    deleterow_query = f"DELETE FROM {table_name} WHERE {column_name} = '{value}'"
                    cursor.execute(deleterow_query)
                    conn.commit()
                    print(f"The {value} has been deleted successfully.")
                    return True
        except pymysql.Error as e:
            print(f"Error inserting data: {e}")
            return False

    def list_tables(self):
        """
        列出数据库中所有的表格名称

        Returns:
        - 表格名称列表
        """
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SHOW TABLES")
                    tables = [table[0] for table in cursor.fetchall()]
                    return tables
        except pymysql.Error as e:
            print(f"Error listing tables: {e}")

    def get_table_structure(self, table_name):
        """
        获取指定表格的结构，包括列名、数据类型等信息

        Args:
        - table_name: 表格名称

        Returns:
        - 表格结构信息（列名、数据类型）的列表
        """
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"SHOW COLUMNS FROM {table_name}")
                    structure = [(column[0], column[1]) for column in cursor.fetchall()]
                    return structure
        except pymysql.Error as e:
            print(f"Error getting table structure: {e}")

    def count_records(self, table_name):
        """
        获取指定表格中记录的数量

        Args:
        - table_name: 表格名称

        Returns:
        - 记录数量
        """
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    return count
        except pymysql.Error as e:
            print(f"Error counting records: {e}")

    def delete_data_by_condition(self, table_name, condition):
        """
        根据指定条件删除表格中的数据

        Args:
        - table_name: 表格名称
        - condition: 删除条件，例如 "age > 30"

        Returns:
        - 无
        """
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    delete_query = f"DELETE FROM {table_name} WHERE {condition}"
                    cursor.execute(delete_query)
                    conn.commit()
                    print(f"Data matching condition '{condition}' deleted successfully.")
        except pymysql.Error as e:
            print(f"Error deleting data by condition: {e}")

    def update_data_by_condition(self, table_name, update_values, condition):
        """
        根据指定条件更新表格中的数据

        Args:
        - table_name: 表格名称
        - update_values: 要更新的值和列名的字典，例如 {"age": 25, "name": "John"}
        - condition: 更新条件，例如 "id = 1"

        Returns:
        - 无
        """
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    set_clause = ", ".join([f"{column} = %s" for column in update_values.keys()])
                    update_query = f"UPDATE {table_name} SET {set_clause} WHERE {condition}"
                    cursor.execute(update_query, list(update_values.values()))
                    conn.commit()
                    print(f"Data matching condition '{condition}' updated successfully.")
        except pymysql.Error as e:
            print(f"Error updating data by condition: {e}")





    def password_matching(self, table_name, email, password):
        """
        检查密码是否匹配

        Args:
        - table_name: 表格名称
        - email: 用户邮箱
        - password: 用户输入的密码

        Returns:
        - 是否匹配（True/False），用户名（如果匹配则返回）
        """
        try:
            query = f"SELECT name, password FROM {table_name} WHERE email = %s"
            row = self.db.execute_query(query, email)
            if row:
                db_name, db_password = row[0]
                if db_password == password:
                    return True, db_name
            return False, None
        except pymysql.Error as e:
            print(f"Error during login: {e}")
            return False, None

    def get_auth_code_by_name_email(self, table_name, name, email):
        """
        根据输入的 name 和 email 检测是否匹配，并返回该用户下的 auth_code 数据

        Args:
        - table_name: 表格名称
        - name: 用户名
        - email: 用户邮箱

        Returns:
        - 如果匹配则返回该用户下的 auth_code 数据，否则返回 None
        """
        try:
            query = f"SELECT name, auth_code FROM {table_name} WHERE email = %s"
            result = self.db.execute_query(query, email)
            if result:
                db_name, auth_code = result[0]
                if db_name == name:
                    return auth_code
            return None
        except pymysql.Error as e:
            print(f"Error fetching auth code: {e}")
            return None
    
    def get_password_by_name_email(self, table_name, name, email):
        """
        根据输入的 name 和 email 检测是否匹配，并返回该用户下的 password 数据

        Args:
        - table_name: 表格名称
        - name: 用户名
        - email: 用户邮箱

        Returns:
        - 如果匹配则返回该用户下的 password 数据，否则返回 None
        """
        try:
            query = f"SELECT name, password FROM {table_name} WHERE email = %s"
            result = self.db.execute_query(query, email)
            if result:
                db_name, password = result[0]
                if db_name == name:
                    return password
            else:
                return None
        except pymysql.Error as e:
            print(f"Error fetching auth code: {e}")
            return None

    def insert_data_by_name(self, table_name , name, column_values):
        """
        根据名称定位到数据行，并向该行的其他列插入数据

        Args:
        - table_name: 表格名称
        - name: 指定的名称
        - column_values: 包含要插入的列名和对应值的字典，例如 {"column1": value1, "column2": value2}

        Returns:
        - 无
        """
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    # 构建更新查询语句
                    set_clause = ", ".join([f"{column} = %s" for column in column_values.keys()])
                    update_query = f"UPDATE {table_name} SET {set_clause} WHERE name = %s"
                    # 构建要更新的值列表
                    update_values = list(column_values.values()) + [name]
                    cursor.execute(update_query, update_values)
                    conn.commit()
                    print(f"Data inserted into row where name is '{name}' successfully.")
        except pymysql.Error as e:
            print(f"Error inserting data by name: {e}")

    def check_avatar_by_name(self, table_name, name):
        """
        根据输入的 name 检测 avatar 列是否为空

        Args:
        - table_name: 表格名称
        - name: 用户名

        Returns:
        - 如果 avatar 列不为空则返回 True avatar，否则返回 False
        """
        try:
            query = f"SELECT avatar FROM {table_name} WHERE name = %s"
            result = self.db.execute_query(query, name)
            if result:
                avatar = result[0][0]
                if avatar is not None and avatar != '':
                    return avatar
            return False
        except pymysql.Error as e:
            print(f"Error checking avatar by name: {e}")
            return False
        
    def check_avatar_by_email(self, table_name, email):
        """
        根据输入的 email 检测 avatar 列是否为空

        Args:
        - table_name: 表格名称
        - email: 用户邮箱

        Returns:
        - 如果 avatar 列不为空则返回 True avatar，否则返回 False
        """
        try:
            query = f"SELECT avatar FROM {table_name} WHERE email = %s"
            result = self.db.execute_query(query, email)
            if result:
                avatar = result[0][0]
                if avatar is not None and avatar != '':
                    return avatar
            return False
        except pymysql.Error as e:
            print(f"Error checking avatar by email: {e}")
            return False

    def search_in_table(self, table_name, column_name, search_text):
        """
        在指定的表中搜索包含指定文本的行

        Args:
        - table_name: 表格名称
        - column_name: 要搜索的列名
        - search_text: 要搜索的文本

        Returns:
        - 包含指定文本的行中名字的列表，如果没有找到则返回空列表
        """
        try:
            query = f"SELECT {column_name} FROM {table_name} WHERE {column_name} LIKE %s"
            result = self.db.execute_query(query, '%' + search_text + '%')
            return [row[0] for row in result]
        except pymysql.Error as e:
            print(f"Error searching in table: {e}")
            return []

    def get_user_info_by_name(self, table_name, name):
        """
        根据用户名获取用户所有信息

        Args:
        - table_name: 表格名称
        - name: 用户名

        Returns:
        - 如果找到用户，则返回包含用户所有信息的字典，否则返回 None
        """
        try:
            query = f"SELECT * FROM {table_name} WHERE name = %s"
            result = self.db.execute_query(query, name)
            if result:
                user_info = result[0]
                return {
                    'name': user_info[0],
                    'email': user_info[1],
                    'gender': user_info[5],
                    'age': user_info[6],
                    'location': user_info[7],
                    'bio': user_info[8],
                    'avatar': user_info[9]
                }
            else:
                return None
        except pymysql.Error as e:
            print(f"Error fetching user info by name: {e}")
            return None

    def update_status_by_name(self, name):
        """
        根据用户名找到数据行，并将其status字段值翻转（0变1，1变0）

        Args:
        - name: 指定的用户名

        Returns:
        - 无
        """
        try:
            # 查询当前status值
            query_status = "SELECT status FROM user_data_registered WHERE name = %s"
            current_status = self.db.execute_query(query_status, name)
            if current_status:
                current_status = current_status[0][0]
                # 更新status值
                new_status = 1 if current_status == 0 else 0
                update_query = "UPDATE user_data_registered SET status = %s WHERE name = %s"
                self.db.execute_query(update_query, new_status, name)
                print(f"Status updated for user '{name}' successfully.")
            else:
                print(f"User '{name}' not found.")
        except pymysql.Error as e:
            print(f"Error updating status by name: {e}")

    def check_user_exist(self, table_name, email):
        """
        根据邮箱检测该用户是否已经注册

        Args:
        - table_name: 表格名称
        - email: 用户邮箱

        Returns:
        - 如果用户已经注册则返回 True，否则返回 False
        """
        try:
            query = f"SELECT email FROM {table_name} WHERE email = %s"
            result = self.db.execute_query(query, email)
            if result:
                return True
            return False
        except pymysql.Error as e:
            print(f"Error checking user existence: {e}")
            return False

    def check_room_exist(self, table_name, room_name):
        """
        检测聊天室是否已经存在

        Args:
        - table_name: 表格名称
        - room_name: 聊天室名称

        Returns:
        - 如果聊天室已经存在则返回 True，否则返回 False
        """
        try:
            query = f"SELECT room_name FROM {table_name} WHERE room_name = %s"
            result = self.db.execute_query(query, room_name)
            if result:
                return True
            return False
        except pymysql.Error as e:
            print(f"Error checking room existence: {e}")
            return False
        
    def get_room_info_by_email(self, table_name, email):
        """
        根据邮箱获取房间信息，一个用户可能有多个房间，返回一个列表

        Args:
        - table_name: 表格名称
        - email: 用户邮箱

        Returns:
        - 如果找到房间则返回包含房间信息的列表，否则返回 None
        """
        try:
            query = f"SELECT room_name FROM {table_name} WHERE email = %s"
            result = self.db.execute_query(query, email)
            if result:
                return [row[0] for row in result]
            else:
                return None
        except pymysql.Error as e:
            print(f"Error fetching room info by email: {e}")
            return None
    
    def get_chat_info_by_room(self, room_name):
        """
        根据房间名获取房间中存储的所有行的聊天信息

        Args:
        - room_name: 房间名称

        Returns:
        - 如果找到房间则返回包含聊天信息的列表，否则返回 None
        """
        try:
            query = f"SELECT * FROM {conversion_table_name(room_name)}"
            data = self.db.execute_query(query)
            if data is not None:
                result = [{'MessageContent': row[0], 'Sender': row[1], 'Time': row[2]} for row in data]
                return result
            else:
                return None
        except pymysql.Error as e:
            print(f"Error fetching chat info by room: {e}")
            return None

    
                     


    
    
