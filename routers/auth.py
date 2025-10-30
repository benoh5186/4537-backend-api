from fastapi import APIRouter, HTTPException, Request, Response, status 
from fastapi.responses import JSONResponse
from schemas.user_schema import UserLogin, UserCreate
from pydantic import ValidationError
from database.database import Database
import os 
import jwt
import bcrypt

router = APIRouter()
db = Database(**{"host" : os.getenv("DB_HOST"), "port" : os.getenv("DB_PORT"), 
"user" : os.getenv("DB_USER"), "password" : os.getenv("DB_PASSWORD"), 
"database" : os.getenv("DATABASE")})


@router.post("v1/login/")
async def handle_login(request: Request, response: Response):
    try:
        check_if_already_in_session(request)
        user_info = await request.json()
        login_schema = UserLogin(**user_info)
        validated = validate_login(login_schema)
        if validated:
            create_access_token(response)
            return JSONResponse(
                status_code=200,
                content={
                    "message" : "login success"
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="incorrect password"
            )
    except ValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )


@router.post("v1/signup")
async def handle_signup():
    pass 



async def validate_session(request: Request):
    pass

async def check_if_already_in_session(request: Request):
    
    pass 


def create_access_token():
    
    pass

def validate_login(login_info:UserLogin):
    user = db.find_user(login_info)
    if user:
        user_pw = user["password"]
        if bcrypt.checkpw(login_info.password, user_pw):
            return True
        else:
            return False  

    else:
        return False 

