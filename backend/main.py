import json
from typing import Generator

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from generator_func import run_engine

from research_town.dbs import Idea, Insight, MetaReview, Proposal, Rebuttal, Review

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.post('/process')  # type: ignore
async def process_url(request: Request) -> Response:
    data = await request.json()
    url = data.get('url')
    if not url:
        return JSONResponse({'error': 'URL is required'}, status_code=400)

    def post_process(generator) -> Generator[str, None, None]:
        for progress in generator:
            if isinstance(progress, Insight):
                item = {'type': 'insight', 'content': progress.content}
            elif isinstance(progress, Idea):
                item = {'type': 'idea', 'content': progress.content}
            elif isinstance(progress, Proposal):
                item = {
                    'type': 'proposal',
                    'q1': progress.q1,
                    'q2': progress.q2,
                    'q3': progress.q3,
                    'q4': progress.q4,
                    'q5': progress.q5,
                }
            elif isinstance(progress, Review):
                item = {
                    'type': 'review',
                    'summary': progress.summary,
                    'strength': progress.strength,
                    'weakness': progress.weakness,
                    'ethical_concerns': progress.ethical_concerns,
                    'score': progress.score,
                }
            elif isinstance(progress, Rebuttal):
                item = {'type': 'rebuttal', 'content': progress.content}
            elif isinstance(progress, MetaReview):
                item = {
                    'type': 'metareview',
                    'summary': progress.summary,
                    'strength': progress.strength,
                    'weakness': progress.weakness,
                    'ethical_concerns': progress.ethical_concerns,
                    'decision': 'accept' if progress.decision is True else 'reject',
                }
            else:
                item = {'type': 'error'}

            yield json.dumps(item) + '\n'

    generator = run_engine(url)
    return StreamingResponse(post_process(generator), media_type='application/json')
