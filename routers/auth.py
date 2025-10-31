from fastapi import APIRouter, HTTPException, Request, Response, status 
from fastapi.responses import JSONResponse
from schemas.user_schema import UserLogin, UserCreate, PasswordException
from pydantic import ValidationError
from database.database import Database
from dotenv import load_dotenv
import os 
import jwt
import bcrypt
from datetime import datetime, timedelta

load_dotenv()

router = APIRouter()
db = Database(**{"host" : os.getenv("DB_HOST"), "port" : int(os.getenv("DB_PORT")), 
"user" : os.getenv("DB_USER"), "password" : os.getenv("DB_PASSWORD"), 
"database" : os.getenv("DATABASE")})


@router.post("/api/auth/login/")
async def handle_login(request: Request, response: Response):
    try:
        check_if_already_in_session(request)
        user_info = await request.json()
        login_schema = UserLogin(**user_info)
        user = validate_login(login_schema)
        create_session_cookie(login_schema, response)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "user" : {
                    "email" : user["email"],
                    "is_admin" : user["is_admin"],
                    "api_token" : user["api_usage"]
                } 
            }
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
    except PasswordException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST
        )


@router.post("/api/auth/signup")
async def handle_signup(request: Request):
    try:
        check_if_already_in_session(request) 
        user_data = await request.json()
        signup_schema = UserCreate(**user_data)
        hashed_password = bcrypt.hashpw(signup_schema.password.encode("utf-8"), bcrypt.gensalt())
        hashed_user = {"email" : signup_schema.email, "password" : hashed_password, "is_admin" : signup_schema.is_admin}
        inserted = db.insert_user(hashed_user)
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


def check_if_already_in_session(request: Request):
    jwt_token = request.cookies.get("jwt")
    if jwt_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED
        )

def create_access_token(user_data):
    payload = {
        "email" : user_data.get("email"),
        "iat" : datetime.utcnow(),
        "exp" : datetime.utcnow() + timedelta(minutes=5)
     }
    jwt_token = jwt.encode(payload, algorithm=os.getenv("JWT_ALGORITHM"), key=os.getenv("JWT_SECRET_KEY"))
    return jwt_token

def create_session_cookie(user_data, response: Response):
    jwt_token = create_access_token(user_data)
    response.set_cookie(
        key="jwt",
        value=jwt_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=300
    )

    

def validate_login(login_info:UserLogin):
    user = db.find_user(login_info)
    if user:
        user_pw = user["password"]
        if not bcrypt.checkpw(login_info.password, user_pw):
            raise PasswordException
        return user 

    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED
        )

