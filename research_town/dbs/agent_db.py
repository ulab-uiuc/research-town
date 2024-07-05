import datetime
import json
from xml.etree import ElementTree

import requests
from beartype.typing import Any, Dict, List, Optional

from ..utils.agent_collector import fetch_author_info
from ..utils.paper_collector import get_bert_embedding, neighborhood_search
from .agent_data import AgentProfile
from ..utils.agent_prompter import summarize_research_direction_prompting


class AgentProfileDB(object):
    def __init__(self, config) -> None:
        self.data: Dict[str, AgentProfile] = {}
        self.config = config

    def add(self, agent: AgentProfile) -> None:
        self.data[agent.pk] = agent

    def update(self, agent_pk: str, updates: Dict[str, Optional[str]]) -> bool:
        if agent_pk in self.data:
            for key, value in updates.items():
                if value is not None:
                    setattr(self.data[agent_pk], key, value)
            return True
        return False

    def delete(self, agent_pk: str) -> bool:
        if agent_pk in self.data:
            del self.data[agent_pk]
            return True
        return False

    def get(self, **conditions: Dict[str, Any]) -> List[AgentProfile]:
        result = []
        for agent in self.data.values():
            if all(getattr(agent, key) == value for key, value in conditions.items()):
                result.append(agent)
        return result

    def match(
        self, idea: str, agent_profiles: List[AgentProfile], num: int = 1
    ) -> List[str]:
        idea_embed = get_bert_embedding([idea])
        bio_list = []
        for agent_profile in agent_profiles:
            if agent_profile.bio is not None:
                bio_list.append(agent_profile.bio)
            else:
                bio_list.append('')
        profile_embed = [embed_.embed for embed_ in agent_profiles]
        index_l = neighborhood_search(
            idea_embed, profile_embed, num).reshape(-1)
        index_all = list(index_l)
        match_pk = []
        for index in index_all:
            match_pk.append(agent_profiles[index].pk)
        return match_pk

    def save_to_file(self, file_name: str) -> None:
        with open(file_name, 'w') as f:
            json.dump(
                {aid: agent.model_dump() for aid, agent in self.data.items()},
                f,
                indent=2,
            )

    def load_from_file(self, file_name: str) -> None:
        with open(file_name + '.json', 'r') as f:
            self.data = json.load(f)

    def update_db(self, data: Dict[str, List[Dict[str, Any]]]) -> None:
        for date, agents in data.items():
            for agent_data in agents:
                agent = AgentProfile(**agent_data)
                self.add(agent)

    def fetch_and_add_agents(self, initial_list: List[str]) -> None:
        for name in initial_list:
            print(name)
            agent_profile = AgentProfile(name=name)
            agent_profile.bio = self.get_user_profile(author_name=name)
            papers, collaborators = fetch_author_info(author=name)
            print(collaborators)
            agent_profile.collaborators = collaborators
            self.data[agent_profile.pk] = agent_profile

    def get_user_profile(self, author_name):
        author_query = author_name.replace(' ', '+')
        url = f'http://export.arxiv.org/api/query?search_query=au:{author_query}&start=0&max_results=300'

        response = requests.get(url)
        papers_list = []
        if response.status_code == 200:
            root = ElementTree.fromstring(response.content)
            entries = root.findall('{http://www.w3.org/2005/Atom}entry')

            total_papers = 0

            papers_by_year = {}

            for entry in entries:
                title = entry.find(
                    '{http://www.w3.org/2005/Atom}title').text.strip()
                published = entry.find(
                    '{http://www.w3.org/2005/Atom}published'
                ).text.strip()
                abstract = entry.find(
                    '{http://www.w3.org/2005/Atom}summary'
                ).text.strip()
                authors_elements = entry.findall(
                    '{http://www.w3.org/2005/Atom}author')
                authors = [
                    author.find('{http://www.w3.org/2005/Atom}name').text
                    for author in authors_elements
                ]
                # Get the paper link
                link = entry.find(
                    '{http://www.w3.org/2005/Atom}id').text.strip()

                # Check if the specified author is exactly in the authors list
                if author_name in authors:
                    # Remove the specified author from the coauthors list for display
                    coauthors = [
                        author for author in authors if author != author_name]
                    coauthors_str = ', '.join(coauthors)

                    papers_list.append(
                        {
                            'date': published,
                            'Title & Abstract': f'{title}; {abstract}',
                            'coauthors': coauthors_str,
                            'link': link,  # Add the paper link to the dictionary
                        }
                    )
                authors_elements = entry.findall(
                    '{http://www.w3.org/2005/Atom}author')
                authors = [
                    author.find('{http://www.w3.org/2005/Atom}name').text
                    for author in authors_elements
                ]

                if author_name in authors:
                    total_papers += 1
                    published_date = entry.find(
                        '{http://www.w3.org/2005/Atom}published'
                    ).text.strip()
                    date_obj = datetime.datetime.strptime(
                        published_date, '%Y-%m-%dT%H:%M:%SZ'
                    )

                    year = date_obj.year
                    if year not in papers_by_year:
                        papers_by_year[year] = []
                    papers_by_year[year].append(entry)

            if total_papers > 40:
                for cycle_start in range(
                    min(papers_by_year), max(papers_by_year) + 1, 5
                ):
                    cycle_end = cycle_start + 4
                    for year in range(cycle_start, cycle_end + 1):
                        if year in papers_by_year:
                            selected_papers = papers_by_year[year][:2]
                            for paper in selected_papers:
                                title = paper.find(
                                    '{http://www.w3.org/2005/Atom}title'
                                ).text.strip()
                                abstract = paper.find(
                                    '{http://www.w3.org/2005/Atom}summary'
                                ).text.strip()
                                authors_elements = paper.findall(
                                    '{http://www.w3.org/2005/Atom}author'
                                )
                                co_authors = [
                                    author.find(
                                        '{http://www.w3.org/2005/Atom}name'
                                    ).text
                                    for author in authors_elements
                                    if author.find(
                                        '{http://www.w3.org/2005/Atom}name'
                                    ).text
                                    != author_name
                                ]

                                papers_list.append(
                                    {
                                        'Author': author_name,
                                        'Title & Abstract': f'{title}; {abstract}',
                                        'Date Period': f'{year}',
                                        'Cycle': f'{cycle_start}-{cycle_end}',
                                        'Co_author': ', '.join(co_authors),
                                    }
                                )

            papers_list = papers_list[:10]
            personal_info = '; '.join(
                [f"{details['Title & Abstract']}" for details in papers_list]
            )
            info = summarize_research_direction_prompting(
                personal_info=personal_info,
                prompt_template=self.config.prompt_template.summarize_research_direction,
            )
            return info
        else:
            print('Failed to fetch data from arXiv.')
            return ''
