import random

from research_town.dbs import AgentProfileDB, PaperProfileDB
from research_town.utils.agent_collector import fetch_author_info

agent_db = AgentProfileDB()

domain = 'computer vision'
initial_list = [
    'Kaiming He',
    'Ross Girshick',
    'Li Fei-Fei',
    'Jia Deng',
    'Ali Farhadi',
    'Richard Szeliski',
]

final_list = []
for name in initial_list:
    _, coauthor = fetch_author_info(name)
    sample_size = len(coauthor) // 5
    sample_coauthor = random.sample(coauthor, sample_size)
    final_list.extend(sample_coauthor)

final_list.extend(initial_list)
final_list = list(set(final_list))

agent_db.fetch_and_add_agents(final_list)
agent_db.save_to_file('data/agent_data/' + domain + '.json')

paper_db = PaperProfileDB()

domain = 'computer vision'

paper_db.fetch_and_add_papers(10, domain)

paper_db.save_to_file('data/paper_data/' + domain + '.json')
