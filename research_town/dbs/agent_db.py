import datetime
import json
from xml.etree import ElementTree

import requests
from beartype.typing import Any, Dict, List, Optional
from transformers import BertModel, BertTokenizer

from ..configs import Config
from ..utils.agent_collector import fetch_author_info
from ..utils.agent_prompter import summarize_research_direction_prompting
from ..utils.paper_collector import neighborhood_search
from ..utils.retriever import get_bert_embedding
from .agent_data import AgentProfile


class AgentProfileDB(object):
    def __init__(self) -> None:
        self.data: Dict[str, AgentProfile] = {}
        self.retriever_tokenizer: BertTokenizer = BertTokenizer.from_pretrained(
            'facebook/contriever'
        )
        self.retriever_model: BertModel = BertModel.from_pretrained(
            'facebook/contriever'
        )

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
        idea_embed = get_bert_embedding(
            instructions=[idea],
            retriever_tokenizer=self.retriever_tokenizer,
            retriever_model=self.retriever_model,
        )
        bio_list = []
        for agent_profile in agent_profiles:
            if agent_profile.bio is not None:
                bio_list.append(agent_profile.bio)
            else:
                bio_list.append('')
        profile_embed = get_bert_embedding(
            instructions=bio_list,
            retriever_tokenizer=self.retriever_tokenizer,
            retriever_model=self.retriever_model,
        )
        index_l = neighborhood_search(idea_embed, profile_embed, num)
        index_all = [index for index_list in index_l for index in index_list]
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
        with open(file_name, 'r') as f:
            data = json.load(f)
            self.data = {
                aid: AgentProfile(**agent_data) for aid, agent_data in data.items()
            }

    def update_db(self, data: Dict[str, List[Dict[str, Any]]]) -> None:
        for date, agents in data.items():
            for agent_data in agents:
                agent = AgentProfile(**agent_data)
                self.add(agent)

    def fetch_and_add_agents(self, initial_list: List[str], config: Config) -> None:
        for name in initial_list:
            print(name)
            agent_profile = AgentProfile(name=name)
            agent_profile.bio = self.get_user_profile(author_name=name, config=config)[
                0
            ]
            papers, collaborators = fetch_author_info(author=name)
            print(collaborators)
            agent_profile.collaborators = collaborators
            self.data[agent_profile.pk] = agent_profile

    def get_user_profile(self, author_name: str, config: Config) -> List[str]:
        author_query = author_name.replace(' ', '+')
        url = f'http://export.arxiv.org/api/query?search_query=au:{author_query}&start=0&max_results=300'

        response = requests.get(url)
        papers_list = []
        root = ElementTree.fromstring(response.content)
        entries = root.findall('{http://www.w3.org/2005/Atom}entry')
        total_papers = 0
        papers_by_year: Dict[Any, List[Any]] = {}
        for entry in entries:
            title_element = entry.find('{http://www.w3.org/2005/Atom}title')
            title = (
                title_element.text.strip()
                if title_element is not None and title_element.text is not None
                else None
            )
            published_element = entry.find(
                '{http://www.w3.org/2005/Atom}published')
            published = (
                published_element.text.strip()
                if published_element is not None and published_element.text is not None
                else None
            )
            abstract_element = entry.find(
                '{http://www.w3.org/2005/Atom}summary')
            abstract = (
                abstract_element.text.strip()
                if abstract_element is not None and abstract_element.text is not None
                else None
            )

            authors_elements = entry.findall(
                '{http://www.w3.org/2005/Atom}author')
            authors = []
            for author in authors_elements:
                author_element = author.find(
                    '{http://www.w3.org/2005/Atom}name')
                if author_element is not None:
                    authors.append(author_element.text)
            link_element = entry.find('{http://www.w3.org/2005/Atom}id')
            link = (
                link_element.text.strip()
                if link_element is not None and link_element.text is not None
                else None
            )
            # Check if the specified author is exactly in the authors list
            if author_name in authors:
                # Remove the specified author from the coauthors list for display
                coauthors = [
                    author
                    for author in authors
                    if author is not None and author != author_name
                ]
                coauthors_str = ', '.join(coauthors) if coauthors else ''
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
            authors = []
            for author in authors_elements:
                author_element = author.find(
                    '{http://www.w3.org/2005/Atom}name')
                if author_element is not None:
                    authors.append(author_element.text)
            if author_name in authors:
                total_papers += 1
                published_date_element = entry.find(
                    '{http://www.w3.org/2005/Atom}published'
                )
                published_date = (
                    published_date_element.text.strip()
                    if published_date_element is not None
                    and published_date_element.text is not None
                    else None
                )
                date_obj = (
                    datetime.datetime.strptime(
                        published_date, '%Y-%m-%dT%H:%M:%SZ')
                    if published_date is not None
                    else None
                )

                year = date_obj.year if date_obj is not None else None
                if year not in papers_by_year:
                    papers_by_year[year] = []
                papers_by_year[year].append(entry)

        if total_papers > 40:
            for cycle_start in range(min(papers_by_year), max(papers_by_year) + 1, 5):
                cycle_end = cycle_start + 4
                for year in range(cycle_start, cycle_end + 1):
                    if year in papers_by_year:
                        selected_papers = papers_by_year[year][:2]
                        for paper in selected_papers:
                            title_element = paper.find(
                                '{http://www.w3.org/2005/Atom}title'
                            )

                            title = (
                                title_element.text.strip()
                                if title_element is not None
                                and title_element.text is not None
                                else None
                            )
                            abstract_element = paper.find(
                                '{http://www.w3.org/2005/Atom}summary'
                            )

                            abstract = (
                                abstract_element.text.strip()
                                if abstract_element is not None
                                and abstract_element.text is not None
                                else None
                            )

                            authors_elements = paper.findall(
                                '{http://www.w3.org/2005/Atom}author'
                            )

                            co_authors = []
                            for author in authors_elements:
                                author_element = author.find(
                                    '{http://www.w3.org/2005/Atom}name'
                                )
                                if author_element is not None:
                                    if (
                                        author_element.text is not None
                                        and author_element.text != author_name
                                    ):
                                        co_authors.append(author_element.text)

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
            prompt_template=config.prompt_template.summarize_research_direction,
        )
        return info
