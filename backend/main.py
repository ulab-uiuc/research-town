import asyncio
import json
import multiprocessing
import uuid
from typing import AsyncGenerator, Generator, List, Optional, Tuple, Union

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from generator_func import run_engine

from research_town.agents import Agent
from research_town.data import Idea, Insight, MetaReview, Proposal, Rebuttal, Review

app = FastAPI()
ProgressList = Union[
    List[Insight],
    List[Idea],
    List[Proposal],
    List[Review],
    List[Rebuttal],
    List[MetaReview],
]

# Enable CORS for all origins, credentials, methods, and headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

active_processes: dict[str, multiprocessing.Process] = {}


def stop_process(user_id: str) -> None:
    if user_id in active_processes:
        process = active_processes[user_id]
        process.terminate()  # Safely terminate the process
        process.join()  # Ensure cleanup
        del active_processes[user_id]
        print(f'Process for user {user_id} stopped.')


def background_task(
    url: str, child_conn: multiprocessing.connection.Connection
) -> None:
    generator = run_engine(url)
    try:
        for progress, agent in generator:
            child_conn.send((progress, agent))
    except Exception as e:
        child_conn.send({'type': 'error', 'content': str(e)})
    finally:
        child_conn.send(None)
        child_conn.close()


def generator_wrapper(
    result: Tuple[Optional[ProgressList], Optional[Agent]],
) -> Generator[Tuple[Optional[ProgressList], Optional[Agent]], None, None]:
    yield result


def format_response(
    generator: Generator[Tuple[Optional[ProgressList], Optional[Agent]], None, None],
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


@app.post('/process')  # type: ignore
async def process_url(request: Request) -> StreamingResponse | JSONResponse:
    # Get URL from the request body
    data = await request.json()
    url = data.get('url')

    # Return error if URL is not provided
    if not url:
        return JSONResponse({'error': 'URL is required'}, status_code=400)

    # Generate a unique user ID for the task
    user_id = str(uuid.uuid4())

    # Create a multiprocessing Pipe for communication
    parent_conn, child_conn = multiprocessing.Pipe()

    # Start the background task as a separate process
    process = multiprocessing.Process(target=background_task, args=(url, child_conn))
    process.start()

    # Store the process for later tracking
    active_processes[user_id] = process
    print(f'Task for user {user_id} started.')

    async def stream_response() -> AsyncGenerator[str, None]:
        try:
            while True:
                if await request.is_disconnected():
                    print(f'Client disconnected for user {user_id}. Cancelling task.')
                    stop_process(user_id)
                    break

                if parent_conn.poll():
                    result = parent_conn.recv()
                    if result is None:
                        break

                    for formatted_output in format_response(generator_wrapper(result)):
                        yield formatted_output
                else:
                    await asyncio.sleep(0.1)
        finally:
            stop_process(user_id)  # Ensure process is stopped on function exit

    # Return the StreamingResponse
    return StreamingResponse(stream_response(), media_type='application/json')
