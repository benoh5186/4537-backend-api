from fastapi import APIRouter, HTTPException, Request, status, Response
from .auth import AuthUtility
import httpx

class Admin:
    def __init__(self, db):
        self.__router = APIRouter()
        self.__db = db
        self.__add_routes()
        
    def __add_routes(self):
        self.__router.add_api_route(path="/api/admin/user/{uid}", endpoint=self.__handle_user_delete, methods=["DELETE"])
        self.__router.add_api_route(path="/api/admin/users", endpoint=self.__handle_get_users, methods=["GET"])
        
    def get_router(self):
        return self.__router
    
    async def __handle_user_delete(self, uid: int, request: Request):
        payload = AuthUtility.authenticate(request)
        is_admin = AuthUtility.check_is_admin(payload, self.__db)
        
        if is_admin:
            AdminUtility.delete_user(uid, self.__db)
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required",
            )
        
        return Response(
            status_code=status.HTTP_200_OK, 
            detail="User deleted"
            )
        
    async def __handle_get_users(self, request: Request):
        payload = AuthUtility.authenticate(request)
        is_admin = AuthUtility.check_is_admin(payload, self.__db)
        
        if is_admin:
            return AdminUtility.get_users(self.__db)
        else:
           raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required",
            ) 
            
        
class AdminUtility:
    @staticmethod
    def delete_user(uid, db):
        deleted = db.delete_user(uid)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
            
    @staticmethod
    def get_users(db):
        return db.get_users_with_usage()
        
            
            