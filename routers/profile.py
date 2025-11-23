from fastapi import APIRouter, HTTPException, Request, status
from .auth import AuthUtility



class ProfileRouter:
    def __init__(self, db):
        self.__router = APIRouter()
        self.__db = db 
    


    async def __change_password(self, request: Request):
        user_data = await request.json()
        jwt_active = AuthUtility.authenticate(request)
        if jwt_active:
            payload = AuthUtility.get_jwt_payload(request)
            uid = payload["sub"]
            user_data = await request.json()
            
