from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth
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

routers = [
    auth.AuthRouter(db_info).get_router()
]

class App:
    """
    Application class for configuring and managing the FastAPI instance.
    """
    def __init__(self):
        """
        Initialize an App instance with a FastAPI application and configure middleware.
        """
        self.__app = FastAPI()
        self.__add_middleware()
        self.__app.exception_handlers
    
    def __add_middleware(self):
        """
        Configure CORS middleware.
        """
        self.__app.add_middleware(
                CORSMiddleware,
                allow_origins=["https://4537-project-frontend.netlify.app"],
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
app_instance.add_routers(routers)

app = app_instance.get_app()

