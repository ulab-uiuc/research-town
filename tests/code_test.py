from agent_base import BaseResearchAgent
from kb_base import BaseKnowledgeBase

base_agent = BaseResearchAgent("Jiaxuan You")
# print(base_agent.profile)

kb = BaseKnowledgeBase()
# print(kb.get_data(10,"Machine Learning"))
data = kb.get_data(10, "Machine Learning")
paper = base_agent.read_paper(data, "Machine Learning")
idea = base_agent.generate_idea(data, "Machine Learning")
relations = base_agent.get_co_author_relationships("Jiaxuan You", 3)
