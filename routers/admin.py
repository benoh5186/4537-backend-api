from fastapi import APIRouter, HTTPException, Request, status, Response
from .auth import AuthUtility

class Admin:
    """
    Router class handling administrative operations such as deleting users,
    retrieving all users, and retrieving API endpoint usage statistics.
    """
    __DELETE_USER_ENDPOINT = "/api/v1/admin/user/{uid}"
    __GET_ALL_USERS_ENDPOINT = "/api/v1/admin/users"
    __GET_ALL_ENDPOINTS_ENDPOINT = "/api/v1/admin/endpoints"

    def __init__(self, db):
        """
        Initialize an Admin router instance with database access.

        :param db: database instance used for executing admin-level operations
        """
        self.__router = APIRouter()
        self.__db = db
        self.__add_routes()
        
    def __add_routes(self):
        """
        Register admin-specific API routes to the router.
        """
        self.__router.add_api_route(path=self.__DELETE_USER_ENDPOINT, endpoint=self.__handle_user_delete, methods=["DELETE"])
        self.__router.add_api_route(path=self.__GET_ALL_USERS_ENDPOINT, endpoint=self.__handle_get_users, methods=["GET"])
        self.__router.add_api_route(path=self.__GET_ALL_ENDPOINTS_ENDPOINT, endpoint=self.__handle_get_endpoints, methods=["GET"])
        
    def get_router(self):
        """
        Return the configured APIRouter instance.

        :return: the APIRouter object with registered admin routes
        """
        return self.__router
    
    async def __handle_user_delete(self, uid: int, request: Request):
        """
        Handle user deletion requests for a given uid.

        This endpoint verifies admin privileges and deletes the specified user if found.

        :param uid: integer identifying the user to delete
        :param request: the incoming HTTP request object
        :return: an empty response with status code 204 upon successful deletion
        :raises HTTPException: if requester is not admin or user does not exist
        """
        endpoint_info = {"method" : "DELETE", "endpoint" : self.__DELETE_USER_ENDPOINT}
        self.__db.update_endpoint(endpoint_info)
        payload = AuthUtility.authenticate(request)
        is_admin = AuthUtility.check_is_admin(payload, self.__db)
        
        if is_admin:
            AdminUtility.delete_user(uid, self.__db)
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required",
            )
        
        return Response(status_code=status.HTTP_204_NO_CONTENT)
        
    async def __handle_get_users(self, request: Request):
        """
        Handle requests for retrieving all users along with their API usage counts.

        This endpoint verifies admin privileges before returning user data.

        :param request: the incoming HTTP request object
        :return: a list of users with usage information
        :raises HTTPException: if requester is not admin
        """
        endpoint_info = {"method" : "GET", "endpoint" : self.__GET_ALL_USERS_ENDPOINT}
        self.__db.update_endpoint(endpoint_info)
        payload = AuthUtility.authenticate(request)
        is_admin = AuthUtility.check_is_admin(payload, self.__db)
        
        if is_admin:
            return AdminUtility.get_users(self.__db)
        else:
           raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required",
            ) 

    async def __handle_get_endpoints(self, request: Request):
        """
        Handle endpoint statistics retrieval requests.

        This returns all API endpoints and their tracked request counts.

        :param request: the incoming HTTP request object
        :return: a list of endpoint usage statistics
        :raises HTTPException: if requester is not admin
        """
        endpoint_info = {"method" : "GET", "endpoint" : self.__GET_ALL_ENDPOINTS_ENDPOINT}
        self.__db.update_endpoint(endpoint_info)
        payload = AuthUtility.authenticate(request)
        is_admin = AuthUtility.check_is_admin(payload, self.__db)

        if is_admin:
            return AdminUtility.get_endpoints(self.__db)
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required",
            ) 

        
class AdminUtility:
    """
    Utility class providing static methods for administrative operations
    such as deleting users, retrieving user lists, and retrieving endpoint statistics.
    """
    @staticmethod
    def delete_user(uid, db):
        """
        Delete a user from the database.

        :param uid: integer representing the user's unique identifier
        :param db: database instance used to perform deletion
        :raises HTTPException: if the user does not exist
        """
        deleted = db.delete_user(uid)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
            
    @staticmethod
    def get_users(db):
        """
        Retrieve all users along with their API usage counts.

        :param db: database instance used to retrieve user data
        :return: a list of dictionaries representing users and usage stats
        """

        return db.get_users_with_usage()


    @staticmethod
    def get_endpoints(db):
        """
        Retrieve all tracked API endpoints and their request statistics.

        :param db: database instance used to retrieve endpoint statistics
        :return: a list of dictionaries containing endpoint usage data
        """
        return db.get_all_endpoints()
        
            
            