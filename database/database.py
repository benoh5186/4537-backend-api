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
        """
        Retrieve the current API usage count for a user.

        If no usage row exists for the user, a new row is created with the default
        usage count of 0.

        :param uid: integer representing the user's unique identifier
        :return: integer representing the user's API usage count
        """
        if self.__connection is None:
            self.start_database()

        query = """SELECT usage_count FROM api_usage WHERE uid = %s"""
        self.__cursor.execute(query, (uid,))
        usage = self.__cursor.fetchone()

        if usage is None:
            # No row yet:  create one with default 0
            insert_query = """INSERT INTO api_usage (uid, usage_count) VALUES (%s, 0)"""
            self.__cursor.execute(insert_query, (uid,))
            self.__connection.commit()
            return 0

        return usage["usage_count"]

    def increment_api_usage(self, uid):
        """
        Increment the API usage count for a specific user by 1.
        
        :param uid: integer representing the user's unique identifier
        """
        if self.__connection is None:
            self.start_database()
        query = """UPDATE api_usage SET usage_count = usage_count + 1 WHERE uid = %s"""
        self.__cursor.execute(query, (uid,))
        self.__connection.commit()
    
    def change_password(self, uid, hashed_password):
        """
        Update the password for a specific user.

        :param uid: integer representing the user's unique identifier
        :param hashed_password: string containing the newly hashed password
        """
        if self.__connection is None:
            self.start_database()
        query = """UPDATE user SET password = %s WHERE uid = %s"""
        self.__cursor.execute(query, (hashed_password, uid))
        self.__connection.commit()


    def change_email(self, uid, email):
        """
        Update the email address for a specific user.

        :param uid: integer representing the user's unique identifier
        :param email: string containing the new email address
        :return: True if update succeeded, False if email is already in use
        """

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
        """
        Delete a user and all associated API usage data from the database.

        :param uid: integer representing the user's unique identifier
        :return: True if a user was deleted, False otherwise
        """
        if self.__connection is None:
            self.start_database()

        # Delete dependent rows first
        self.__cursor.execute("DELETE FROM api_usage WHERE uid = %s", (uid,))

        query = "DELETE FROM user WHERE uid = %s"
        rows = self.__cursor.execute(query, (uid,))
        self.__connection.commit()
        return rows > 0

    def update_endpoint(self, endpoint_info):
        """
        Update or create an API request count entry for a given endpoint.

        If the endpoint already exists in the table, its request_count is incremented.
        Otherwise, a new row is inserted with an initial count of 1.

        :param endpoint_info: dictionary containing 'method' and 'endpoint' keys
        """
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
        """
        Retrieve all endpoint request statistics from the database.

        :return: a list of dictionaries containing endpoint usage data
        """
        if self.__connection is None:
            self.start_database()
        query = """SELECT * FROM api_request_stats"""
        self.__cursor.execute(query)
        data = self.__cursor.fetchall()
        return data 

    def get_users_with_usage(self):
        """
        Retrieve all users along with their API usage counts.

        This method performs a join between the user table and the api_usage table
        to return combined information for each user.

        :return: list of dictionaries containing user and usage data
        """
        if self.__connection is None:
            self.start_database()

        query = """
            SELECT
                user.uid,
                user.email,
                user.is_admin,
                api_usage.usage_count AS api_usage
            FROM user
            JOIN api_usage
                ON user.uid = api_usage.uid;

        """
        self.__cursor.execute(query)
        users = self.__cursor.fetchall()  # list of dicts because of DictCursor

        for user in users:
            user["is_admin"] = bool(user["is_admin"])

        return users

            


