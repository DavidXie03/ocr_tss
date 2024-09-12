import pymysql
from contextlib import closing
import app


class User:
    def __init__(self, host='127.0.0.1', port=3306, user='root', passwd='20030404ab', db='user_message', charset='utf8'):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.db = db
        self.charset = charset
        self.connection = self.connect()

    def connect(self):
        """建立数据库连接"""
        return pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            passwd=self.passwd,
            db=self.db,
            charset=self.charset
        )

    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()

    def execute_sql(self, sql):
        """执行 SQL 语句"""
        with closing(self.connect()) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute(sql)
                results = cursor.fetchall()
                connection.commit()
                return results

    def check_account_exists(self, account):
        """检查账号是否存在"""
        sql_check = "SELECT * FROM user WHERE account = %s"
        with closing(self.connect()) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute(sql_check, (account,))
                return cursor.fetchone() is not None

    def register(self, account, password):
        """注册新账户"""
        if self.check_account_exists(account):
            # print("该账号已存在，请重新输入！")
            return False
        else:
            sql_insert = "INSERT INTO user (account, password) VALUES (%s, %s)"
            with closing(self.connect()) as connection:
                with closing(connection.cursor()) as cursor:
                    cursor.execute(sql_insert, (account, password))
                    connection.commit()
                    # print("账号注册成功！")
                    return True

    def login(self, account, password):
        """验证用户登录"""
        sql_query = "SELECT * FROM user WHERE account = %s AND password = %s"
        with closing(self.connect()) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute(sql_query, (account, password))
                result = cursor.fetchone()
                if result:
                    print("登录成功！")
                    return result[0]
                else:
                    print("账号或密码错误！")
                    return 0

    def get_user_id(self, account, password):
        """获取用户的 user_id"""
        return self.login(account, password)


# 使用示例
if __name__ == '__main__':
    user_manager = User()
    uploader = app.Uploader()

    # 注册账户
    #account = input("请输入账号：")
    #password = input("请输入密码：")
    #if user_manager.register(account, password):
    #    print("注册成功！")
    #else:
    #    print("注册失败，请尝试其他账号。")

    # 登录账户
    account = input("请输入账号: ")
    password = input("请输入密码: ")
    #user_id = user_manager.get_user_id(account, password)
    #if user_id:
    #    print("登录成功！")
    #else:
    #    print("登录失败，请检查您的账号和密码。")

    user_manager.store(uploader)

    user_manager.close()  # 关闭数据库连接