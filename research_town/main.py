from function_class import *

single_agent = SingleAgent()
# print(single_agent.get_profile("Jiaxuan You"))
# print(single_agent.get_recent_paper_info(10,"Machine Learning"))
# domain="Machine Learning"
# profile=single_agent.get_profile("Jiaxuan You")
# papers=single_agent.get_recent_paper_info(10,"Machine Learning")
#
# ideas=single_agent.generate_ideas(profile,papers,domain)
# print(ideas)

multi_agent = MultiAgent()
print(multi_agent.get_relation_graph("Jiaxuan You", 20))
