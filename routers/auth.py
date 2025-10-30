from fastapi import APIRouter, HTTPException, Form, Request, Response
import jwt

router = APIRouter()

@router.post("v1/login/")
async def handle_login(request: Request):
    try:
        check_if_already_in_session(request)
        

        pass
    except:
        pass


@router.post("v1/signup")
async def handle_signup():
    pass 



async def validate_session(request: Request):
    pass

async def check_if_already_in_session(request: Request):
    
    pass 


def create_access_token():
    
    pass

