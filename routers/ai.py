from fastapi import APIRouter, HTTPException, Request, status
from .auth import AuthUtility
import httpx


router = APIRouter()


@router.post("/api/service/ai")
async def handle_ai_json(request: Request):
    is_auth = AuthUtility.authenticate(request)
    if is_auth:
        body = await request.json()
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://four537-ai-backend.onrender.com/v1/json/parse",
                json={"text" : body["text"], "lang" : body["lang"]}
            )
            if response.is_success:
                data = response.json()
                return {"data" : data["data"]}
            else:
                raise HTTPException(
                    # 400
                    status_code=response.status_code,
                    detail={
                        "message" : "nah"
                    }
                )
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
            

