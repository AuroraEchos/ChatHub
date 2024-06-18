
import pymysql

class Database:
    def __init__(self, host='127.0.0.1', port=3306, user='root', passwd='root123', charset='utf8', db=None):
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

# 测试云主机连接
hosts_to_test = ['']

for host in hosts_to_test:
    db = Database(host=host, user='root', passwd='', db='basicinformation')
    print(f"Testing connection to host: {host}")
    try:
        with db.connect() as conn:
            print("Connection successful!")
    except pymysql.Error as e:
        print(f"Connection failed with error: {e}")
