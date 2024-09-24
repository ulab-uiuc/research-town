import json
from typing import Generator, Tuple

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from generator_func import run_engine

from research_town.agents import Agent
from research_town.dbs import (
    Idea,
    Insight,
    MetaReview,
    Progress,
    Proposal,
    Rebuttal,
    Review,
)

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

    def post_process(
        generator: Generator[Tuple[Progress, Agent], None, None],
    ) -> Generator[str, None, None]:
        for progress, agent in generator:
            if isinstance(progress, Insight):
                item = {'type': 'insight', 'content': progress.content}
            elif isinstance(progress, Idea):
                item = {'type': 'idea', 'content': progress.content}
            elif isinstance(progress, Proposal):
                item = {
                    'type': 'proposal',
                    'q1': progress.q1 if progress.q1 else '',
                    'q2': progress.q2 if progress.q2 else '',
                    'q3': progress.q3 if progress.q3 else '',
                    'q4': progress.q4 if progress.q4 else '',
                    'q5': progress.q5 if progress.q5 else '',
                }
            elif isinstance(progress, Review):
                item = {
                    'type': 'review',
                    'summary': progress.summary if progress.summary else '',
                    'strength': progress.strength if progress.strength else '',
                    'weakness': progress.weakness if progress.weakness else '',
                    'ethical_concerns': progress.ethical_concerns
                    if progress.ethical_concerns
                    else '',
                    'score': str(progress.score) if progress.score else '-1',
                }
            elif isinstance(progress, Rebuttal):
                item = {'type': 'rebuttal', 'content': progress.content}
            elif isinstance(progress, MetaReview):
                item = {
                    'type': 'metareview',
                    'summary': progress.summary if progress.summary else '',
                    'strength': progress.strength if progress.strength else '',
                    'weakness': progress.weakness if progress.weakness else '',
                    'ethical_concerns': progress.ethical_concerns
                    if progress.ethical_concerns
                    else '',
                    'decision': 'accept' if progress.decision is True else 'reject',
                }
            else:
                item = {'type': 'error'}

            if agent is not None:
                item['agent_name'] = agent.profile.name

            print(item)
            yield json.dumps(item) + '\n'

    generator = run_engine(url)
    return StreamingResponse(post_process(generator), media_type='application/json')
