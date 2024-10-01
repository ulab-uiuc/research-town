import json
from typing import Generator, List, Optional, Tuple, Union

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from generator_func import run_engine

from research_town.agents import Agent
from research_town.data import Idea, Insight, MetaReview, Proposal, Rebuttal, Review

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
        generator: Generator[
            Tuple[
                Union[
                    List[Insight],
                    List[Idea],
                    List[Proposal],
                    List[Review],
                    List[Rebuttal],
                    List[MetaReview],
                    None,
                ],
                Optional[Agent],
            ],
            None,
            None,
        ],
    ) -> Generator[str, None, None]:
        for progress, agent in generator:
            if not progress:
                continue
            for prog in progress:
                item = {}
                if prog is None or agent is None:
                    item = {
                        'type': 'error',
                        'content': 'Failed to collect complete paper content from the link.',
                    }
                elif isinstance(prog, Insight):
                    item = {'type': 'insight', 'content': prog.content}
                elif isinstance(prog, Idea):
                    item = {'type': 'idea', 'content': prog.content}
                elif isinstance(prog, Proposal):
                    item = {
                        'type': 'proposal',
                        'q1': prog.q1 or '',
                        'q2': prog.q2 or '',
                        'q3': prog.q3 or '',
                        'q4': prog.q4 or '',
                        'q5': prog.q5 or '',
                    }
                elif isinstance(prog, Review):
                    item = {
                        'type': 'review',
                        'summary': prog.summary or '',
                        'strength': prog.strength or '',
                        'weakness': prog.weakness or '',
                        'ethical_concerns': prog.ethical_concerns or '',
                        'score': str(prog.score) if prog.score else '-1',
                    }
                elif isinstance(prog, Rebuttal):
                    item = {
                        'type': 'rebuttal',
                        'q1': prog.q1 or '',
                        'q2': prog.q2 or '',
                        'q3': prog.q3 or '',
                        'q4': prog.q4 or '',
                        'q5': prog.q5 or '',
                    }
                elif isinstance(prog, MetaReview):
                    item = {
                        'type': 'metareview',
                        'summary': prog.summary or '',
                        'strength': prog.strength or '',
                        'weakness': prog.weakness or '',
                        'ethical_concerns': prog.ethical_concerns or '',
                        'decision': 'accept' if prog.decision else 'reject',
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
