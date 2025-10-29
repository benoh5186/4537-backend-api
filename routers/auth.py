from fastapi import APIRouter, HTTPException, Form, Request, Response
import jwt


router = APIRouter()


@router.post("v1/login/")
def handle_login():
    pass


@router.post("v1/signup")
def handle_signup():
    pass 
