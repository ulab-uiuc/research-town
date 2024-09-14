# frontend/backend/main.py
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from generator_function import data_generator

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/process")
async def process_url(request: Request):
    data = await request.json()
    url = data.get('url')
    if not url:
        return {"error": "URL is required"}

    generator = data_generator(url)
    return StreamingResponse(generator, media_type="text/plain")
