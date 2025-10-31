from operator import methodcaller
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

    def __init__(self, db_info):
        """
        Initialize an AuthRouter with database connection information.
        
        :param db_info: a dictionary containing database connection parameters
        """
        self.__router = APIRouter()
        self.__db = Database(**db_info)
        self.__add_routes()

    def __add_routes(self):
        """
        Register authentication API routes to the router.
        """
        self.__router.add_api_route(path="/api/auth/login/", endpoint=self.__handle_login, methods=["POST"])
        self.__router.add_api_route(path="/api/auth/signup", endpoint=self.__handle_signup, methods=["POST"])
        self.__router.add_api_route(path="/api/auth/session", endpoint=self.__handle_session, methods=["GET"]) 
    
    def get_router(self):
        """
        Return the configured APIRouter instance.
        
        :return: the APIRouter object with registered authentication routes
        """
        return self.__router

    async def __handle_session(self, request: Request):
        """
        Handle session verification requests by checking for a valid JWT cookie.
        
        :param request: the incoming HTTP request object
        :return: a JSON response indicating session status
        :raises HTTPException: if no valid JWT token is found in cookies
        """
        jwt_token = request.cookies.get("jwt")
        print(jwt_token)
        if jwt_token:
            return {JSONResponse(
                status_code=status.HTTP_200_OK,
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
        """
        Handle user registration requests by validating input and creating a new user account.
        
        :param request: the incoming HTTP request containing user registration data
        :return: a JSON response indicating successful account creation
        :raises HTTPException: if validation fails or user already exists
        """
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
            "email" : user_data["email"],
            "api_usage" : user_data["api_usage"],
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
            secure=False,
            samesite="lax",
            max_age=300
        )

    @staticmethod
    def get_jwt_payload(request: Request):
        """
        Decodes jwt token from cookies and returns payload.

        Payload includes email address, api usage, creation time (iat), and expiration time (exp)

        :param request: HTTP request
        :return: payload data from decoding jwt
        """
        try:
            jwt_token = request.cookies.get("jwt")
            payload = jwt.decode(jwt=jwt_token, key=os.getenv("JWT_SECRET_KEY"), algorithms=os.getenv("JWT_ALGORITHM"))
            return payload 
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

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
            return user 
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED
            )

