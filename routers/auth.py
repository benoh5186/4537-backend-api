from fastapi import APIRouter, HTTPException, Request, Response, status 
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK
from schemas.user_schema import UserLogin, UserCreate, PasswordException
from pydantic import ValidationError
from database.database import Database
import os 
import jwt
import bcrypt
from datetime import datetime, timedelta


class AuthRouter:

    def __init__(self, db_info):
        self.__router = APIRouter()
        self.__db = Database(**db_info)
        self.__add_routes()

    def __add_routes(self):
        self.__router.add_api_route(path="/api/auth/login/", endpoint=self.__handle_login, methods=["POST"])
        self.__router.add_api_route(path="/api/auth/signup", endpoint=self.__handle_signup, methods=["POST"])
        self.__router.add_api_route(path="/api/auth/session", endpoint=self.__handle_session, methods=["GET"]) 
    
    def get_router(self):
        return self.__router

    async def __handle_session(self, request: Request):
        jwt_token = request.cookies.get("jwt")
        print(jwt_token)
        if jwt_token:
            return {JSONResponse(
                status_code=HTTP_200_OK,
                content={
                    "message" : "in session"
                }
            )}
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "message" : "not in session"
                }
                
            )


    async def __handle_login(self, request: Request, response: Response):
        try:
            user_info = await request.json()
            login_schema = UserLogin(**user_info)
            AuthUtility.validate_login(login_schema, self.__db)
            AuthUtility.create_session_cookie(login_schema, response)
            print(response.headers.get("set_cookie"))
            return {"message" : "login success"}
        except ValidationError as error:
            detail = {"email" : True, "password" : True}
            field_errors = [err['loc'][-1] for err in error.errors()]
            for field in field_errors:
                if field in detail:
                    detail[field] = False

            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=detail
            )
        except PasswordException:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
    async def __handle_signup(self, request: Request):
        try:
            user_data = await request.json()
            signup_schema = UserCreate(**user_data)
            hashed_password = bcrypt.hashpw(signup_schema.password.encode("utf-8"), bcrypt.gensalt())
            hashed_user = {"email" : signup_schema.email, "password" : hashed_password, "is_admin" : signup_schema.is_admin}
            inserted = self.__db.insert_user(hashed_user)
            if inserted:
                return JSONResponse(
                    status_code=status.HTTP_201_CREATED,
                    content={
                        "message": "sign up successful"
                    }
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT
                )
        except ValidationError as error:
            detail = {"email" : True, "password" : True}
            field_errors = [err['loc'][-1] for err in error.errors()]
            for field in field_errors:
                if field in detail:
                    detail[field] = False
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=detail
            )




class AuthUtility:

    @staticmethod
    def create_access_token(user_data: UserLogin):
        payload = {
            "email" : user_data.email,
            "iat" : datetime.utcnow(),
            "exp" : datetime.utcnow() + timedelta(minutes=5)
         }
        jwt_token = jwt.encode(payload, algorithm=os.getenv("JWT_ALGORITHM"), key=os.getenv("JWT_SECRET_KEY"))
        return jwt_token

    @staticmethod
    def create_session_cookie(user_data: UserLogin, response: Response):
        jwt_token = AuthUtility.create_access_token(user_data)
        response.set_cookie(
            key="jwt",
            value=jwt_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=300
        )

    @staticmethod
    def validate_login(login_info:UserLogin, db):
        user = db.find_user(login_info)
        if user:
            user_pw_bytes = user["password"].encode('utf-8')
            login_password_bytes = login_info.password.encode('utf-8')
            if not bcrypt.checkpw(login_password_bytes, user_pw_bytes):
                raise PasswordException
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED
            )

