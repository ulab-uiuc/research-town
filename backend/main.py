from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

from .generator_func import run_engine

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.post('/process') # type: ignore
async def process_url(request: Request) -> Response:
    data = await request.json()
    url = data.get('url')
    if not url:
        return JSONResponse({'error': 'URL is required'}, status_code=400)

    generator = run_engine(url)
    return StreamingResponse(generator, media_type='text/plain')
