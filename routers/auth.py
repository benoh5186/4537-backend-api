from fastapi import APIRouter, HTTPException, Form, Request, Response, status 
from schemas.user_schema import UserLogin, UserCreate
from pydantic import ValidationError
from database.database import Database
import os 
import jwt

router = APIRouter()
db = Database(**{"host" : os.getenv("DB_HOST"), "port" : os.getenv("DB_PORT"), 
"user" : os.getenv("DB_USER"), "password" : os.getenv("DB_PASSWORD"), 
"database" : os.getenv("DATABASE")})


@router.post("v1/login/")
async def handle_login(request: Request):
    try:
        check_if_already_in_session(request)
        user_info = await request.json()
        user_schema = UserLogin(**user_info)
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
        pass 

    else:
        return False 

