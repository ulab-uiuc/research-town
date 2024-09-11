from typing import List

import os
import gradio as gr
from research_town.configs import Config
from research_town.dbs import LogDB, PaperDB, ProgressDB, ResearcherDB, Proposal
from research_town.engines import Engine
from research_town.utils.paper_collector import get_paper_content


def get_proposals(introduction) -> List[str]:
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
    # if save path exists, then load
    config = Config(config_file_path)
    agent_db = ResearcherDB()
    paper_db = PaperDB()
    if os.path.exists(save_file_path):
        agent_db.load_from_json(save_file_path, with_embed=True)
        paper_db.load_from_json(save_file_path, with_embed=True)
    else:
        agent_db.pull_agents(agent_names=agent_names, config=config)
        paper_db.pull_papers(num=10, domain='graph neural networks')

    env_db = LogDB()
    progress_db = ProgressDB()
    engine = Engine(
        project_name='research_town_demo',
        agent_db=agent_db,
        paper_db=paper_db,
        progress_db=progress_db,
        env_db=env_db,
        config=config,
    )
    engine.run(task=introduction)
    proposals = progress_db.get(Proposal)
    contents = [proposal.abstract for proposal in proposals]
    return contents

def get_introduction(url) -> str:
    contents = get_paper_content(url)
    section_contents = contents[0]
    for section_name, section_content in section_contents.items():
        if 'Introduction' in section_name:
            return section_content

with gr.Blocks() as demo:
    input_url = gr.Textbox(label='input')

    @gr.render(inputs=[input_url], triggers=[input_url.submit])  # type: ignore
    def show_proposals(url):
        if 'https://www.arxiv.org' not in url:
            gr.Markdown('We only accept arxiv links.')
        else:
            introduction = get_introduction(url)
            proposals = get_proposals(introduction)
            for proposal in proposals:
                gr.Textbox(proposal)


demo.launch()
