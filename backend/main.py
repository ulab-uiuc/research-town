# frontend/backend/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from backend.generator import run_engine

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.post('/process')
async def process_url(request: Request):
    data = await request.json()
    url = data.get('url')
    if not url:
        return {'error': 'URL is required'}

    generator = run_engine(url)
    return StreamingResponse(generator, media_type='text/plain')
