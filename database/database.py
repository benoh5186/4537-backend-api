import pymysql
from schemas.user_schema import UserLogin


"""
Database module for managing MySQL database connections and user operations.

This module provides the Database class which handles database connectivity, user retrieval, user creation, and table initialization for the application.
"""


class Database:
    """
    Database class handling MySQL database connections and user-related operations.
    """
    def __init__(self, **kwargs):
        """
        Initialize a Database instance with connection parameters.
        
        :param kwargs: keyword arguments containing database connection information (host, port, user, password, database)
        """
        self.__connection = None
        self.__data = kwargs 
        self.__cursor = None

    def start_database(self):
        """
        Establish a connection to the MySQL database and create the user table if it doesn't exist.
        """
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
        """
        Find and retrieve a user from the database by email address.
        
        :param user_info: a UserLogin object containing the user's email
        :return: a dictionary containing user data if found, None otherwise
        """
        if self.__connection is None:
            self.start_database()
        query = "SELECT * FROM user WHERE  email = %s"
        self.__cursor.execute(query, (user_info.email, ))
        user = self.__cursor.fetchone()
        return user 

    def user_exists(self, user_info):
        """
        Check if a user exists in the database by email address.
        
        :param user_info: a dictionary containing the user's email
        :return: True if the user exists, False otherwise
        """
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
        """
        Insert a new user into the database with email, password, and admin status.
        
        :param user_info: a dictionary containing email, password, and is_admin fields
        :return: True if insertion was successful, False if user already exists
        """
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
        """
        Create the user table in the database if it does not already exist.
        """
        query = """CREATE TABLE IF NOT EXISTS user (
                uid INT(11) AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                is_admin BOOL NOT NULL DEFAULT FALSE,
                api_usage INT NOT NULL DEFAULT 20
                ) ENGINE=InnoDB;
            """
        self.__cursor.execute(query)