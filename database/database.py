import pymysql
import os 
from schemas.user_schema import UserCreate, UserLogin


class Database:
    def __init__(self, **kwargs) -> None:
        self.__connection = pymysql.connect(
            host=kwargs["host"],
            user=kwargs["user"],
            password=kwargs["password"],
            database=kwargs["database"],
            cursorclass=pymysql.cursors.DictCursor
        )
        self.__cursor = self.__connection.cursor()
        self.__create_table()

    def find_user(self, user_info: UserLogin):
        query = "SELECT * FROM user WHERE  email = %s"
        self.__cursor.execute(query, (user_info.email, ))
        user = self.__cursor.fetchone()
        return user 

    def user_exists(self, user_info):
        query = "SELECT * FROM user WHERE email = %s"
        self.__cursor.execute(query, (user_info["email"], ))
        user = self.__cursor.fetchone()
        if user:
            return True
        else:
            return False 

    def insert_user(self, user_info: UserCreate):
        try:
            query = """INSERT INTO user (email, password, is_admin) VALUES (%s %s %s)"""
            self.__cursor.execute(query, (user_info.email, user_info.password, user_info.is_admin))
            self.__cursor.commit() 
            return True 
        except pymysql.IntegrityError:
            self.__cursor.rollback()
            return False

    def __create_table(self):
        query = """CREATE TABLE IF NOT EXISTS user (
                uid INT(11) AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                is_admin BOOL NOT NULL DEFAULT FALSE,
                API_USAGE INT NOT NULL DEFAULT 30
                ) ENGINE=InnoDB;
            """
        self.__cursor.execute(query)