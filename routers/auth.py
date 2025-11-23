from fastapi import APIRouter, HTTPException, Request, Response, status 
from fastapi.responses import JSONResponse
from schemas.user_schema import UserLogin, UserCreate, PasswordException
from pydantic import ValidationError
from database.database import Database
import os 
import jwt
import bcrypt
from datetime import datetime, timedelta

"""
Authentication router module for handling user login, signup, and session management.

This module provides the AuthRouter class which implements authentication endpoints and the AuthUtility class for JWT token generation and credential validation.
"""


class AuthRouter:
    """
    Router class handling authentication endpoints for login, signup, and session management.
    """

    __AUTHENTICATE_ENDPOINT = "/api/v1/auth/authenticate"
    __LOGIN_ENDPOINT = "/api/v1/auth/login"
    __SIGNUP_ENDPOINT = "/api/v1/auth/signup"

    def __init__(self, db):
        """
        Initialize an AuthRouter with database connection information.
        
        :param db_info: a dictionary containing database connection parameters
        """
        self.__router = APIRouter()
        self.__db = db
        self.__add_routes()

    def __add_routes(self):
        """
        Register authentication API routes to the router.
        """
        self.__router.add_api_route(path=self.__LOGIN_ENDPOINT, endpoint=self.__handle_login, methods=["POST"])
        self.__router.add_api_route(path=self.__SIGNUP_ENDPOINT, endpoint=self.__handle_signup, methods=["POST"])
        self.__router.add_api_route(path=self.__AUTHENTICATE_ENDPOINT, endpoint=self.__authenticate, methods=["GET"]) 
        # self.__router.add_api_route(path="/{full_path:path}", endpoint=self.__authenticate, methods=["OPTIONS"]) 

    def get_router(self):
        """
        Return the configured APIRouter instance.
        
        :return: the APIRouter object with registered authentication routes
        """
        return self.__router

    async def __authenticate(self, request: Request):
        """
        Handle session verification requests by checking for a valid JWT cookie.
        
        :param request: the incoming HTTP request object
        :return: a JSON response indicating session status
        :raises HTTPException: if no valid JWT token is found in cookies
        """
        payload = AuthUtility.authenticate(request)
        print(f"the payload is {payload}")
        endpoint_info = {"method" : "GET", "endpoint" : self.__AUTHENTICATE_ENDPOINT}
        self.__db.update_endpoint(endpoint_info)
        if payload:
            uid = int(payload["sub"])
            user_info = self.__db.find_user(uid)
            is_admin = bool(user_info["is_admin"])
            api_usage = self.__db.get_api_usage(uid)
            email = user_info["email"]
            
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "is_admin" : is_admin,
                    "api_usage" : api_usage,
                    "email" : email
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "message" : "unauthorized"
                }
                
            )

    async def __handle_login(self, request: Request, response: Response):
        """
        Handle user login requests by validating credentials and creating a session cookie.
        
        :param request: the incoming HTTP request containing user login credentials
        :param response: the HTTP response object to set the session cookie
        :return: a dictionary with a success message
        :raises HTTPException: if validation fails or credentials are incorrect
        """
        try:
            user_info = await request.json()
            login_schema = UserLogin(**user_info)
            
            user = AuthUtility.validate_login(login_schema, self.__db)
            AuthUtility.create_session_cookie(user, response)
            
            print(response.headers.get("set_cookie"))
            endpoint_info = {"method" : "POST", "endpoint" : self.__LOGIN_ENDPOINT}
            self.__db.update_endpoint(endpoint_info)
            return {"message" : "login success", "is_admin" : user["is_admin"]}
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
        """
        Handle user registration requests by validating input and creating a new user account.
        
        :param request: the incoming HTTP request containing user registration data
        :return: a JSON response indicating successful account creation
        :raises HTTPException: if validation fails or user already exists
        """
        try:
            endpoint_info = {"method" : "POST", "endpoint" : self.__SIGNUP_ENDPOINT}
            self.__db.update_endpoint(endpoint_info)
            user_data = await request.json()
            signup_schema = UserCreate(**user_data)
            
            hashed_password = bcrypt.hashpw(signup_schema.password.encode("utf-8"), bcrypt.gensalt()).decode('utf-8')
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
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User already exists"
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
            
    # # TODO: Make a cleaner version of the explicit preflight handler
    # async def __preflight_handler(request: Request, full_path: str):
    #     response = JSONResponse(content={"ok": True})
    #     origin = request.headers.get("origin")

    #     # TODO: better to check if origin is part of the allowed origins first
    #     if origin in ["https://4537-project-frontend.netlify.app", "http://localhost:8000"]:
    #         response.headers["Access-Control-Allow-Origin"] = origin
    #         response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
    #         response.headers["Access-Control-Allow-Headers"] = request.headers.get(
    #             "access-control-request-headers", ""
    #         )
    #         response.headers["Access-Control-Allow-Credentials"] = "true"
    #     return response



class AuthUtility:
    """
    Utility class providing static methods for authentication operations including token generation and validation.
    """

    @staticmethod
    def create_access_token(user_data):
        """
        Create a JWT access token for an authenticated user.

        payload includes email address and api usage 
        
        :param user_data: dict containing user credentials
        :return: an encoded JWT token string
        """
        payload = {
            "sub" : str(user_data["uid"]),
            "iat" : datetime.utcnow(),
            "exp" : datetime.utcnow() + timedelta(minutes=5)
         }
        jwt_token = jwt.encode(payload, algorithm=os.getenv("JWT_ALGORITHM"), key=os.getenv("JWT_SECRET_KEY"))
        return jwt_token

    @staticmethod
    def create_session_cookie(user_data, response: Response):
        """
        Create and set a session cookie with a JWT token in the HTTP response.
        
        :param user_data: dict containing user credentials
        :param response: the HTTP response object to attach the cookie to
        """

        jwt_token = AuthUtility.create_access_token(user_data)
        response.set_cookie(
            key="jwt",
            value=jwt_token,
            httponly=True,
            secure=True,
            samesite="none",
            max_age=300,
            path="/"
        )

    @staticmethod
    def validate_login(login_info:UserLogin, db):
        """
        Validate user login credentials against stored database records.
        
        :param login_info: a UserLogin object containing email and password
        :param db: the database instance to query for user information
        :raises PasswordException: if the password does not match
        :raises HTTPException: if the user is not found in the database
        """
        user = db.find_user(login_info.email)
        if user:
            user_pw_bytes = user["password"].encode('utf-8')
            login_password_bytes = login_info.password.encode('utf-8')
            if not bcrypt.checkpw(login_password_bytes, user_pw_bytes):
                raise PasswordException
            user["is_admin"] = bool(user["is_admin"])
            return user 
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED
            )

    @staticmethod
    def authenticate(request:Request):
        """
        Decodes jwt token from cookies and returns payload.

        :param request: HTTP request
        :return: payload data from decoding jwt
        """
        jwt_token = request.cookies.get("jwt")
        if jwt_token is None:
            raise HTTPException(status_code=401, detail="Not authenticated")

        try:
            payload = jwt.decode(
                jwt_token,
                key=os.getenv("JWT_SECRET_KEY"),
                algorithms=[os.getenv("JWT_ALGORITHM")],
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        
    @staticmethod 
    def increase_api_usage(payload, db):
        uid = payload["sub"]   
        db.increment_api_usage(uid)
        
    @staticmethod
    def get_api_usage(payload, db):
        uid = payload["sub"]
        return db.get_api_usage(uid)
    
    @staticmethod
    def check_is_admin(payload, db):
        uid = payload["sub"]
        user = db.find_user(uid)
        if user:
            return bool(user["is_admin"])
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

            

