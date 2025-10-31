import pymysql
import os 
from schemas.user_schema import UserCreate, UserLogin


class Database:
    def __init__(self, **kwargs) -> None:
        self.__connection = None
        self.__data = kwargs 
        self.__cursor = None

    def start_database(self):
        self.__connection = pymysql.connect(
            host=self.__data["host"],
            port=self.__data["port"],
            user=self.__data["user"],
            password=self.__data["password"],
            database=self.__data["database"],
            cursorclass=pymysql.cursors.DictCursor,
            ssl={'ssl': True})
        self.__cursor = self.__connection.cursor()
        self.__create_table()

    def find_user(self, user_info: UserLogin):
        if self.__connection is None:
            self.start_database()
        query = "SELECT * FROM user WHERE  email = %s"
        self.__cursor.execute(query, (user_info.email, ))
        user = self.__cursor.fetchone()
        return user 

    def user_exists(self, user_info):
        if self.__connection is None:
            self.start_database()
        query = "SELECT * FROM user WHERE email = %s"
        self.__cursor.execute(query, (user_info["email"], ))
        user = self.__cursor.fetchone()
        if user:
            return True
        else:
            return False 

    def insert_user(self, user_info):
        try:
            if self.__connection is None:
                self.start_database()
            query = """INSERT INTO user (email, password, is_admin) VALUES (%s, %s, %s)"""
            self.__cursor.execute(query, (user_info["email"], user_info["password"], user_info["is_admin"]))
            self.__connection.commit() 
            return True 
        except pymysql.IntegrityError:
            self.__connection.rollback()
            return False

    def __create_table(self):
        query = """CREATE TABLE IF NOT EXISTS user (
                uid INT(11) AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                is_admin BOOL NOT NULL DEFAULT FALSE,
                api_usage INT NOT NULL DEFAULT 20
                ) ENGINE=InnoDB;
            """
        self.__cursor.execute(query)