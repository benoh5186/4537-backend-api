from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth
import os 

load_dotenv()

db_info = {"host" : os.getenv("DB_HOST"), "port" : int(os.getenv("DB_PORT")), 
"user" : os.getenv("DB_USER"), "password" : os.getenv("DB_PASSWORD"), 
"database" : os.getenv("DATABASE")}

routers = [
    auth.AuthRouter(db_info).get_router()
]

class App:
    def __init__(self):
        self.__app = FastAPI()
        self.__add_middleware()
    
    def __add_middleware(self):
        self.__app.add_middleware(
                CORSMiddleware,
                allow_origins=["http://localhost:3000"],
                allow_credentials=True,
                allow_methods=["*"]
            )
    def add_routers(self, routers):
        for router in routers:
            self.__app.include_router(router)

    def get_app(self):
        return self.__app

app_instance = App()
app_instance.add_routers(routers)

app = app_instance.get_app()

