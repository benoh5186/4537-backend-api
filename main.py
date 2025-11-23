from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from database.database import Database
from routers import auth, ai, profile, admin
import os 

"""
Main application module for initializing and configuring the FastAPI application.

This module sets up the FastAPI instance, configures CORS middleware,
loads environment variables, and registers all API routers.
"""

load_dotenv()

db_info = {"host" : os.getenv("DB_HOST"), "port" : int(os.getenv("DB_PORT")), 
"user" : os.getenv("DB_USER"), "password" : os.getenv("DB_PASSWORD"), 
"database" : os.getenv("DATABASE")}

db = Database(**db_info)

routers = [
    auth.AuthRouter(db).get_router(), 
    ai.AI(db).get_router(),
    profile.ProfileRouter(db).get_router(),
    admin.Admin(db).get_router()
]


class App:
    """
    Application class for configuring and managing the FastAPI instance.
    """
    def __init__(self):
        """
        Initialize an App instance with a FastAPI application and configure middleware.
        """
        self.origins = [
            "https://4537-project-frontend.netlify.app", 
            "http://localhost:8000", # Local host server 
            "http://127.0.0.1:5500", # Live server
            "http://127.0.0.1:8080", # AI backend local host 
        ]                       
        self.__app = FastAPI()
        # TODO: Temporary fix for CORS Middleware issue
        self.__add_middleware()
        self.add_routers(routers)
    
    def __add_middleware(self):
        """
        Configure CORS middleware.
        """
        self.__app.add_middleware(
                CORSMiddleware,
                allow_origins=self.origins,
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"]
            )

    def add_routers(self, routers):
        """
        Register a list of API routers to the FastAPI app.
        
        :param routers: a list of APIRouter objects to be included in the app
        """

        for router in routers:
            self.__app.include_router(router)

    def get_app(self):
        """
        Return the FastAPI instance.
        
        :return: the FastAPI application object
        """
        return self.__app

app_instance = App()
# app_instance.add_routers(routers)

app = app_instance.get_app()

