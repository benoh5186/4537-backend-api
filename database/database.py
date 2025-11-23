from unicodedata import unidata_version
import bcrypt
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

    def find_user(self, identifier):
        """
        Find and retrieve a user from the database by email address or uid.
        
        :param identifier: string representing user's email address or uid
        :return: a dictionary containing user data if found, None otherwise
        """
        if self.__connection is None:
            self.start_database()
        if isinstance(identifier, int):
            query = "SELECT * FROM user WHERE  uid = %s"
        else:
            query = "SELECT * FROM user WHERE  email = %s"
        self.__cursor.execute(query, (identifier, ))
        user = self.__cursor.fetchone()
        return user 

    

    def user_exists(self, user_info):
        """
        Check if a user exists in the database by email address.
        
        :param user_email: a dictionary containing the user's email
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
            user_query = """INSERT INTO user (email, password, is_admin) VALUES (%s, %s, %s)"""
            api_usage_query = """INSERT INTO api_usage (uid) VALUES (%s)"""
            self.__cursor.execute(user_query, (user_info["email"], user_info["password"], user_info["is_admin"]))
            uid = self.__cursor.lastrowid
            self.__cursor.execute(api_usage_query, (uid,))
            self.__connection.commit() 
            return True 
        except pymysql.IntegrityError:
            self.__connection.rollback()
            return False

    def get_api_usage(self, uid):
        if self.__connection is None:
            self.start_database()
        query = """SELECT usage_count FROM api_usage WHERE uid = %s"""
        self.__cursor.execute(query, (uid,))
        usage = self.__cursor.fetchone()
        return usage["usage_count"]

    def increment_api_usage(self, uid):
        if self.__connection is None:
            self.start_database()
        query = """UPDATE api_usage SET usage_count = usage_count + 1 WHERE uid = %s"""
        self.__cursor.execute(query, (uid,))
        self.__connection.commit()
    
    def change_password(self, uid, hashed_password):
        if self.__connection is None:
            self.start_database()
        query = """UPDATE user SET password = %s WHERE uid = %s"""
        self.__cursor.execute(query, (hashed_password, uid))
        self.__connection.commit()


    def change_email(self, uid, email):

        if self.__connection is None:
            self.start_database()
        try:
            query = """UPDATE user SET email = %s WHERE uid = %s"""
            self.__cursor.execute(query, (email, uid))
            self.__connection.commit()
            return True
        except pymysql.IntegrityError:
            self.__connection.rollback()
            return False
        
    def delete_user(self, uid):
        if self.__connection is None:
            self.start_database()
        query = "DELETE FROM user WHERE uid = %s"
        rows = self.__cursor.execute(query, (uid,))
        self.__connection.commit()
        return rows > 0

    def update_endpoint(self, endpoint_info):
        if self.__connection is None:
            self.start_database()
        query = """
        INSERT INTO api_request_stats (http_method, endpoint, request_count)
        VALUES (%s, %s, 1)
        ON DUPLICATE KEY UPDATE request_count = request_count + 1;
        """
        self.__cursor.execute(query, (endpoint_info["method"], endpoint_info["endpoint"]))
        self.__connection.commit()

    def get_all_endpoints(self):
        if self.__connection is None:
            self.start_database()
        query = """SELECT * FROM api_request_stats"""
        self.__cursor.execute(query)
        data = self.__cursor.fetchall()
        return data 

    def get_users_with_usage(self):
        if self.__connection is None:
            self.start_database()

        query = """
            SELECT
                u.uid,
                u.email,
                u.is_admin,
                COALESCE(a.api_usage, 0) AS api_usage
            FROM user AS u
            LEFT JOIN api AS a
                ON u.uid = a.uid;
        """
        self.__cursor.execute(query)
        users = self.__cursor.fetchall()  # list of dicts because of DictCursor
        for user in users:
            user["is_admin"] = bool(user["is_admin"])
        return users
            


