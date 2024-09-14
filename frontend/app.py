import os
from typing import Generator, Optional

import gradio as gr

from research_town.configs import Config
from research_town.dbs import LogDB, PaperDB, ProfileDB, ProgressDB
from research_town.engines import Engine
from research_town.utils.paper_collector import get_paper_content


def get_proposals(introduction: str) -> Optional[str]:
    config_file_path = '../configs'
    save_file_path = '../examples/research_town_demo_log'
    agent_names = [
        'Jiaxuan You',
        'Jure Leskovec',
        'Stefanie Jegelka',
        'Silvio Lattanzi',
        'Rex Ying',
        'Tim Althoff',
        'Christos Faloutsos',
        'Julian McAuley',
    ]
    # Load or initialize databases
    config = Config(config_file_path)
    profile_db = ProfileDB()
    paper_db = PaperDB()
    if os.path.exists(save_file_path):
        profile_db.load_from_json(save_file_path, with_embed=True)
        paper_db.load_from_json(save_file_path, with_embed=True)
    else:
        profile_db.pull_profiles(agent_names=agent_names, config=config)
        paper_db.pull_papers(num=10, domain='graph neural networks')

    log_db = LogDB()
    progress_db = ProgressDB()
    engine = Engine(
        project_name='research_town_demo',
        profile_db=profile_db,
        paper_db=paper_db,
        progress_db=progress_db,
        log_db=log_db,
        config=config,
    )
    engine.start(task=introduction)
    while engine.curr_env.name != 'end':
        run_result = engine.curr_env.run()
        if run_result is not None:
            for progress, agent in run_result:
                engine.time_step += 1
        engine.transition()
    return None


def get_introduction(url: str) -> Optional[str]:
    contents = get_paper_content(url)
    if contents is None or contents[0] is None:
        return None
    section_contents = contents[0]
    for section_name, section_content in section_contents.items():
        if 'Introduction' in section_name:
            return section_content
    return None


def count() -> Generator[int, None, None]:
    for i in range(10):
        yield i


with gr.Blocks() as demo:
    input_url = gr.Textbox(label='input')

    @gr.render(inputs=[input_url], triggers=[input_url.submit])  # type: ignore
    def show_proposals(url):
        if 'arxiv.org' not in url:
            gr.Markdown('We only accept arxiv links.')
        else:
            introduction = get_introduction(url)
            if introduction is None:
                gr.Markdown('Paper parsing error.')
            else:
                config_file_path = '../configs'
                save_file_path = '../examples/research_town_demo_log'
                agent_names = [
                    'Jiaxuan You',
                    'Jure Leskovec',
                    'Stefanie Jegelka',
                    'Silvio Lattanzi',
                    'Rex Ying',
                    'Tim Althoff',
                    'Christos Faloutsos',
                    'Julian McAuley',
                ]
                count_gen = count()
                for num in count_gen:
                    gr.Textbox(num)
                # Load or initialize databases
                config = Config(config_file_path)
                profile_db = ProfileDB()
                paper_db = PaperDB()
                if os.path.exists(save_file_path):
                    profile_db.load_from_json(save_file_path, with_embed=True)
                    paper_db.load_from_json(save_file_path, with_embed=True)
                else:
                    profile_db.pull_profiles(agent_names=agent_names, config=config)
                    paper_db.pull_papers(num=10, domain='graph neural networks')

                for num in count_gen:
                    gr.Textbox(num)
                log_db = LogDB()
                progress_db = ProgressDB()
                engine = Engine(
                    project_name='research_town_demo',
                    profile_db=profile_db,
                    paper_db=paper_db,
                    progress_db=progress_db,
                    log_db=log_db,
                    config=config,
                )
                for i in range(10):
                    gr.Textbox(i)
                engine.start(task=introduction)
                while engine.curr_env.name != 'end':
                    run_result = engine.curr_env.run()
                    if run_result is not None:
                        for progress, agent in run_result:
                            gr.Textbox(
                                'hello'
                            )  # Adjust based on your actual `progress` structure
                            engine.time_step += 1
                    engine.transition()


demo.launch()
