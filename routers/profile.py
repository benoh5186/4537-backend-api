from fastapi import APIRouter, HTTPException, Request, status
from pydantic import ValidationError
from .auth import AuthUtility
from schemas.user_schema import Password, Email
import bcrypt



class ProfileRouter:
    __CHANGE_PASSWORD_ENDPOINT = "/api/v1/user/password"
    __CHANGE_EMAIL_ENDPOINT = "/api/v1/user/email"
    def __init__(self, db):
        self.__router = APIRouter()
        self.__db = db 
        self.__add_routes()


    def __add_routes(self):
        self.__router.add_api_route(path=self.__CHANGE_PASSWORD_ENDPOINT, endpoint=self.__change_password, methods=["PATCH"])
        self.__router.add_api_route(path=self.__CHANGE_EMAIL_ENDPOINT, endpoint=self.__change_email, methods=["PATCH"])
    
    def get_router(self):
        return self.__router


    async def __change_password(self, request: Request):
        endpoint_info = {"method" : "PATCH", "endpoint" : self.__CHANGE_PASSWORD_ENDPOINT}
        self.__db.update_endpoint(endpoint_info)
        payload = AuthUtility.authenticate(request)
        try:
            if payload:
                uid = int(payload["sub"])
                user_data = await request.json()
                password_schema = Password(**user_data)
                if self.__check_password_equality(payload, password_schema.password):
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT)
                hashed_password = bcrypt.hashpw(password_schema.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
                self.__db.change_password(uid, hashed_password)
                return {"message" : "password change success"}
            else:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        except ValidationError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    async def __change_email(self, request: Request):
        endpoint_info = {"method" : "PATCH", "endpoint" : self.__CHANGE_EMAIL_ENDPOINT}
        self.__db.update_endpoint(endpoint_info)
        payload = AuthUtility.authenticate(request)
        try:
            if payload:
                uid = int(payload["sub"])
                user_data = await request.json()
                email_schema = Email(**user_data)
                if self.__check_email_equality(payload, email_schema.email):
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={"same_email" : True})
                is_changed = self.__db.change_email(uid, email_schema.email)
                if is_changed:
                    return {"message" : "email change success", "new_email" : email_schema.email}
                else:
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={"same_email" : False})
            else:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        except ValidationError:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
    
    def __check_email_equality(self, payload, new_email):
        uid = int(payload["sub"])
        user_info = self.__db.find_user(uid)
        if new_email == user_info["email"]:
            return True
        return False 

    def __check_password_equality(self, payload, new_password):
        uid = int(payload["sub"])
        user_info = self.__db.find_user(uid)
        new_password_bytes = new_password.encode('utf-8')
        old_password_bytes = user_info["password"].encode('utf-8')
        if bcrypt.checkpw(new_password_bytes, old_password_bytes):
            return True
        return False





