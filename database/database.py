from unicodedata import unidata_version
import pymysql


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
            ssl={'ssl': True},
            autocommit=False
            )
    
    def ensure_connection(self):
        if self.__connection is None:
            self.start_database()
            return
        try:
            self.__connection.ping(reconnect=True)
        except:
            self.start_database()

    def _fetchone(self, query, params=None):
        self.ensure_connection()
        with self.__connection.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()

    def _fetchall(self, query, params=None):
        self.ensure_connection()
        with self.__connection.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    def _execute(self, query, params=None):
        self.ensure_connection()
        with self.__connection.cursor() as cursor:
            cursor.execute(query, params)
            self.__connection.commit()
            return cursor.lastrowid


    def find_user(self, identifier):
        """
        Find and retrieve a user from the database by email address or uid.
        
        :param identifier: string representing user's email address or uid
        :return: a dictionary containing user data if found, None otherwise
        """
        if isinstance(identifier, int):
            query = "SELECT * FROM user WHERE  uid = %s"
        else:
            query = "SELECT * FROM user WHERE  email = %s"

        return self._fetchone(query, (identifier,)) 

    

    def user_exists(self, user_info):
        """
        Check if a user exists in the database by email address.
        
        :param user_email: a dictionary containing the user's email
        :return: True if the user exists, False otherwise
        """
        query = "SELECT * FROM user WHERE email = %s"
        user = self._fetchone(query, (user_info["email"],))
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
            user_query = """INSERT INTO user (email, password, is_admin) VALUES (%s, %s, %s)"""
            api_usage_query = """INSERT INTO api_usage (uid) VALUES (%s)"""
            uid = self._execute(user_query, (user_info["email"], user_info["password"], user_info["is_admin"]))
            self._execute(api_usage_query, (uid,))
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
        query = """SELECT usage_count FROM api_usage WHERE uid = %s"""
        usage = self._fetchone(query, (uid,))

        # usage can be None because prior to splitting table, the entries did not have corresponding api_usage entry. 
        if usage is None:
            # No row yet:  create one with default 0
            insert_query = """INSERT INTO api_usage (uid, usage_count) VALUES (%s, 0)"""
            self._execute(insert_query, (uid,))
            return 0

        return usage["usage_count"]

    def increment_api_usage(self, uid):
        """
        Increment the API usage count for a specific user by 1.
        
        :param uid: integer representing the user's unique identifier
        """
        query = """UPDATE api_usage SET usage_count = usage_count + 1 WHERE uid = %s"""
        self._execute(query, (uid,))
    
    def change_password(self, uid, hashed_password):
        """
        Update the password for a specific user.

        :param uid: integer representing the user's unique identifier
        :param hashed_password: string containing the newly hashed password
        """
        query = """UPDATE user SET password = %s WHERE uid = %s"""
        self._execute(query, (hashed_password, uid))


    def change_email(self, uid, email):
        """
        Update the email address for a specific user.

        :param uid: integer representing the user's unique identifier
        :param email: string containing the new email address
        :return: True if update succeeded, False if email is already in use
        """
        try:
            query = """UPDATE user SET email = %s WHERE uid = %s"""
            self._execute(query, (email, uid))
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
        # Delete from both tables 
        self._execute("DELETE FROM api_usage WHERE uid = %s", (uid,))

        query = "DELETE FROM user WHERE uid = %s"
        rows = self._execute(query, (uid,))
        return rows > 0

    def update_endpoint(self, endpoint_info):
        """
        Update or create an API request count entry for a given endpoint.

        If the endpoint already exists in the table, its request_count is incremented.
        Otherwise, a new row is inserted with an initial count of 1.

        :param endpoint_info: dictionary containing 'method' and 'endpoint' keys
        """
        query = """
        INSERT INTO api_request_stats (http_method, endpoint, request_count)
        VALUES (%s, %s, 1)
        ON DUPLICATE KEY UPDATE request_count = request_count + 1;
        """
        self._execute(query, (endpoint_info["method"], endpoint_info["endpoint"]))

    def get_all_endpoints(self):
        """
        Retrieve all endpoint request statistics from the database.

        :return: a list of dictionaries containing endpoint usage data
        """
        query = """SELECT * FROM api_request_stats"""
        return self._fetchall(query)
        

    def get_users_with_usage(self):
        """
        Retrieve all users along with their API usage counts.

        This method performs a join between the user table and the api_usage table
        to return combined information for each user.

        :return: list of dictionaries containing user and usage data
        """
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
        users = self._fetchall(query)  # list of dicts because of DictCursor

        for user in users:
            user["is_admin"] = bool(user["is_admin"])

        return users

            


