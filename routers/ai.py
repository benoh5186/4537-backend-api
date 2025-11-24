from fastapi import APIRouter, HTTPException, Request, status
from .auth import AuthUtility
import httpx

class AI:
    """
    Router class handling AI service endpoints for text-to-JSON and schema-based JSON generation.
    """
    __AI_TEXT_TO_JSON_ENDPOINT = "/api/v1/service/ai/text"
    __AI_SCHEMA_TO_JSON_ENDPOINT = "/api/v1/service/ai/schema"


    def __init__(self, db):
        """
        Initialize an AI router instance with the database reference.

        :param db: database instance used for endpoint tracking and user usage updates
        """
        self.__router = APIRouter()
        self.__db = db
        self.__add_routes()
        
    def __add_routes(self):
        """
        Register AI-related API routes to the router.
        """
        self.__router.add_api_route(path=self.__AI_TEXT_TO_JSON_ENDPOINT, endpoint=self.__handle_ai_json, methods=["POST"])
        self.__router.add_api_route(path=self.__AI_SCHEMA_TO_JSON_ENDPOINT, endpoint=self.__handle_ai_schema_json, methods=["POST"])
    
    def get_router(self):
        """
        Return the configured AI APIRouter instance.

        :return: the APIRouter object containing AI service endpoints
        """
        return self.__router
        
    async def __handle_ai_json(self, request: Request):
        """
        Handle requests for converting plain text into structured JSON using the AI backend.

        This endpoint requires authentication and updates the user's API usage count.

        :param request: the incoming HTTP request containing the text and language fields
        :return: a dictionary containing parsed JSON data and updated API usage count
        :raises HTTPException: if the external AI backend returns an error or authentication fails
        """
        
        endpoint_info = {"method" : "POST", "endpoint" : self.__AI_TEXT_TO_JSON_ENDPOINT}
        self.__db.update_endpoint(endpoint_info)
        payload = AuthUtility.authenticate(request)
        AuthUtility.increase_api_usage(payload, self.__db)
        api_usage = AuthUtility.get_api_usage(payload, self.__db)
        if payload:
            body = await request.json()
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://4537-ai-backend-production.up.railway.app/v1/json/parse",
                    json={"text" : body["text"], "lang" : body["lang"]}
                )
                if response.is_success:
                    data = response.json()
                    return {"data" : data["data"], "api_usage" : api_usage}
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

    async def __handle_ai_schema_json(self, request: Request):
        """
        Handle requests for schema-based structured JSON generation using the AI backend.

        This endpoint validates the session, records API usage, and sends the
        provided text, language, and schema to the AI backend for parsing.

        :param request: the incoming HTTP request containing text, language, and JSON schema
        :return: a dictionary with AI-generated structured data and the updated API usage count
        :raises HTTPException: if authentication fails or if the AI backend responds with an error
        """
        endpoint_info = {"method" : "POST", "endpoint" : self.__AI_SCHEMA_TO_JSON_ENDPOINT}
        self.__db.update_endpoint(endpoint_info)
        payload = AuthUtility.authenticate(request)
        AuthUtility.increase_api_usage(payload, self.__db)
        api_usage = AuthUtility.get_api_usage(payload, self.__db)
        if payload:
            body = await request.json()
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://4537-ai-backend-production.up.railway.app/v1/json/schemedParse",
                    json={"text" : body["text"], "lang" : body["lang"], "schema" : body["schema"]}
                )
                if response.is_success:
                    data = response.json()
                    return {"data" : data["data"], "api_usage" : api_usage}
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

            

