import json
from typing import Generator, List, Optional, Tuple

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from generator_func import run_engine

from research_town.agents import Agent
from research_town.data import (
    Idea,
    Insight,
    MetaReview,
    Progress,
    Proposal,
    Rebuttal,
    Review,
)

app = FastAPI()

# Enable CORS for all origins, credentials, methods, and headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.post('/process')  # type: ignore
async def process_url(request: Request) -> Response:
    # Get URL from the request body
    data = await request.json()
    url = data.get('url')

    # Return error if URL is not provided
    if not url:
        return JSONResponse({'error': 'URL is required'}, status_code=400)

    # Helper function to process the generator output
    def format_response(
        generator: Generator[Tuple[Optional[Progress], Optional[Agent]], None, None],
    ) -> Generator[str, None, None]:
        for progress, agent in generator:
            item = {}
            if progress is None or agent is None:
                item = {
                    'type': 'error',
                    'content': 'Failed to collect complete paper content from the link.',
                }
            elif isinstance(progress, Insight):
                item = {'type': 'insight', 'content': progress.content}
            elif isinstance(progress, Idea):
                item = {'type': 'idea', 'content': progress.content}
            elif isinstance(progress, Proposal):
                item = {
                    'type': 'proposal',
                    'q1': progress.q1 or '',
                    'q2': progress.q2 or '',
                    'q3': progress.q3 or '',
                    'q4': progress.q4 or '',
                    'q5': progress.q5 or '',
                }
            elif isinstance(progress, Review):
                item = {
                    'type': 'review',
                    'summary': progress.summary or '',
                    'strength': progress.strength or '',
                    'weakness': progress.weakness or '',
                    'ethical_concerns': progress.ethical_concerns or '',
                    'score': str(progress.score) if progress.score else '-1',
                }
            elif isinstance(progress, Rebuttal):
                item = {
                    'type': 'rebuttal',
                    'q1': progress.q1 or '',
                    'q2': progress.q2 or '',
                    'q3': progress.q3 or '',
                    'q4': progress.q4 or '',
                    'q5': progress.q5 or '',
                }
            elif isinstance(progress, MetaReview):
                item = {
                    'type': 'metareview',
                    'summary': progress.summary or '',
                    'strength': progress.strength or '',
                    'weakness': progress.weakness or '',
                    'ethical_concerns': progress.ethical_concerns or '',
                    'decision': 'accept' if progress.decision else 'reject',
                }
            elif isinstance(progress, List[Review]):
                item = {
                    'type': 'review',
                    'summary': progress[0].summary or '',
                    'strength': progress[0].strength or '',
                    'weakness': progress[0].weakness or '',
                    'ethical_concerns': progress[0].ethical_concerns or '',
                    'score': str(progress[0].score) if progress[0].score else '-1',
                }
            elif isinstance(progress, List[Rebuttal]):
                item = {
                    'type': 'rebuttal',
                    'q1': progress[0].q1 or '',
                    'q2': progress[0].q2 or '',
                    'q3': progress[0].q3 or '',
                    'q4': progress[0].q4 or '',
                    'q5': progress[0].q5 or '',
                }
            elif isinstance(progress, List[MetaReview]):
                item = {
                    'type': 'metareview',
                    'summary': progress[0].summary or '',
                    'strength': progress[0].strength or '',
                    'weakness': progress[0].weakness or '',
                    'ethical_concerns': progress[0].ethical_concerns or '',
                    'decision': 'accept' if progress[0].decision else 'reject',
                }
            else:
                item = {'type': 'error', 'content': 'Unrecognized progress type'}

            if agent:
                item['agent_name'] = agent.profile.name
                if agent.profile.domain is not None:
                    if len(agent.profile.domain) > 1:
                        item['agent_domain'] = agent.profile.domain[0].lower()
                else:
                    item['agent_domain'] = 'computer science'

                if agent.role == 'chair':
                    item['agent_role'] = 'chair'
                elif agent.role == 'reviewer':
                    item['agent_role'] = 'reviewer'
                elif agent.role == 'leader':
                    item['agent_role'] = 'leader'
                elif agent.role == 'member':
                    item['agent_role'] = 'member'
                else:
                    item['agent_role'] = 'none'
            yield json.dumps(item) + '\n'

    # Run the engine and stream the results back
    generator = run_engine(url)
    return StreamingResponse(format_response(generator), media_type='application/json')
