import random

from research_town.dbs import AgentProfileDB, PaperProfileDB
from research_town.utils.agent_collector import fetch_author_info

agent_db = AgentProfileDB()

domain = 'federated learning'
domain_path = domain.replace(' ', '_')
print(domain_path)

initial_list = [
    'Daniel Ramage',
    'H. Brendan McMahan',
    'Song Guo',
    'Yiran Chen',
    'Baochun Li',
    'Nicholas Lane',
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

agent_db.save_to_file('data/agent_data/' + domain_path + '.json')

paper_db = PaperProfileDB()

paper_db.fetch_and_add_papers(10, domain)

paper_db.save_to_file('data/paper_data/' + domain_path + '.json')
