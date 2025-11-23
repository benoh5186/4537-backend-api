from fastapi import APIRouter, HTTPException, Request, status
from .auth import AuthUtility
import httpx

class AI:
    def __init__(self, db):
        self.__router = APIRouter()
        self.__db = db
        self.__add_routes()
        
    def __add_routes(self):
        self.__router.add_api_route(path="/api/service/ai", endpoint=self.__handle_ai_json, methods=["POST"])
        
    async def __handle_ai_json(request: Request):
        is_auth = AuthUtility.authenticate(request)
        if is_auth:
            body = await request.json()
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://4537-ai-backend-production.up.railway.app/v1/json/parse",
                    json={"text" : body["text"], "lang" : body["lang"]}
                )
                if response.is_success:
                    data = response.json()
                    return {"data" : data["data"]}
                else:
                    print("unsuccessful")
                    raise HTTPException(
                        # 400
                        status_code=response.status_code,
                        detail={
                            "message" : "nah"
                        }
                    )
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
            

