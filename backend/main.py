from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from time_estimate import estimate_time
from typing import Optional
from pydantic import BaseModel


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EstimateRequest(BaseModel):
    page_id: str

class EstimateResponse(BaseModel):
    page_id: str
    estimated_time: Optional[int]
    status: str
    message: Optional[str]


class EstimateResponse(BaseModel):
    page_id: str
    status: str
    message: Optional[str]

@app.post("/estimate-time/", response_model=EstimateResponse)
async def estimate_time_endpoint(request: EstimateRequest):
    print('something got', request)
    try:
        await estimate_time(request.page_id)
        
        return {
            "page_id": request.page_id,
            "status": "success", 
            "message": None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при оценке времени: {str(e)}"
        )

@app.get("/health/")
async def health_check():
    return {"status": "ok"}


