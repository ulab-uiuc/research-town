from construct_relation_graph import *
from basic_tool import tools


class SingleAgent:
    def __init__(self):
        self.tools = tools()

    def get_profile(self, name):
        """get user profile through arxiv paper."""
        profile = self.tools.get_user_profile(name)
        return profile

    def get_recent_paper_info(self, num, domain):
        info = self.tools.get_recent_paper(num, domain)
        return info

    def generate_ideas(self, profile, papers, domain):
        """given arxiv paper,generate ideas based on user profile."""
        ideas = self.tools.idea_generation(profile, papers, domain)
        return ideas


class MultiAgent:
    def __init__(self):
        self.tools = tools()

    def get_relation_graph(self, name, max_node):
        """Obtain author-author relations through co-author relationships"""
        start_author = [name]
        graph, node_feat, edge_feat = bfs(author_list=start_author, node_limit=max_node)
        return graph, node_feat, edge_feat
