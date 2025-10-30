import pymysql
import os 
from pydantic import BaseModel, Field,EmailStr, ValidationError

class UserSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    is_admin: bool


class Database:
    def __init__(self, **kwargs) -> None:
        self.__connection = pymysql.connect(
            host=kwargs["host"],
            user=kwargs["user"],
            password=kwargs["password"],
            database=kwargs["database"]
        )
        self.__cursor = self.__connection.cursor()
        self.__table_created = False
    
    def find_user(self, user_info):
        pass

    def user_exists(self, user_info):
        pass

    def insert_user(self, user_info):
        pass 

    def __create_table(self):
        query = """CREATE TABLE IF NOT EXISTS user (
                uid INT(11) AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                is_admin BOOL NOT NULL DEFAULT FALSE
                ) ENGINE=InnoDB;
            """
        self.__cursor.execute(query)