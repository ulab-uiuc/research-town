from beartype import beartype
from beartype.typing import Dict, Generator, List, Union

from ..agents.agent_base import BaseResearchAgent
from ..configs import Config
from ..dbs import (
    AgentProfile,
    AgentProfileDB,
    EnvLogDB,
    PaperProfile,
    PaperProfileDB,
    ResearchPaperSubmission,
)
from .env_base import BaseMultiAgentEnv

LogType = Union[List[Dict[str, str]], None]


class PaperSubmissionMultiAgentEnvironment(BaseMultiAgentEnv):
    def __init__(
        self,
        agent_profiles: List[AgentProfile],
        agent_db: AgentProfileDB,
        paper_db: PaperProfileDB,
        env_db: EnvLogDB,
        config: Config,
        task: Dict[str, str],
    ) -> None:
        super().__init__(agent_profiles)
        self.task = task
        self.paper = PaperProfile()
        self.agent_db = agent_db
        self.paper_db = paper_db
        self.env_db = env_db
        self.config = config

    def _step(
        self,
    ) -> Generator[LogType, None, None]:
        # TODO: support retrieval from database
        # external_data = self.db.get(cls=PaperProfile, conditions={})
        yield from self.log('PaperSubmissionMultiAgentEnvironment started')
        papers = [
            PaperProfile(
                title='A Survey on Machine Learning',
                abstract='This paper surveys the field of machine learning.',
            ),
            PaperProfile(
                title='A Survey on Natural Language Processing',
                abstract='This paper surveys the field of natural language processing.',
            ),
        ]
        agent_names_to_objs: Dict[str, BaseResearchAgent] = {}
        for iter_agent in self.agents:
            if iter_agent.profile.name is not None:
                agent_names_to_objs[iter_agent.profile.name] = iter_agent
        submissions: Dict[str, ResearchPaperSubmission] = {}
        for agent in self.agents:
            yield from self.log(
                f'Agent {agent.profile.name} started finding collaborators'
            )
            # TODO: update find collaborator functions with initial task
            collaborators = agent.find_collaborators(
                paper=PaperProfile(
                    title='A Survey on Machine Learning',
                    abstract='This paper surveys the field of machine learning.',
                ),
                config=self.config,
            )
            collaborator_agents: List[BaseResearchAgent] = []
            for researcher_profile in collaborators:
                if researcher_profile.name:
                    if researcher_profile.name not in agent_names_to_objs:
                        new_agent_obj = BaseResearchAgent(
                            agent_profile=researcher_profile,
                            model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
                        )
                        collaborator_agents.append(new_agent_obj)
                        agent_names_to_objs[researcher_profile.name] = new_agent_obj
                    else:
                        collaborator_agents.append(
                            agent_names_to_objs[researcher_profile.name]
                        )
                    yield from self.log(
                        f'Agent {agent.profile.name} found {researcher_profile.name} as collaborator'
                    )

            insights = agent.read_paper(
                papers=papers,
                domains=['machine learning'],
                config=self.config,
            )
            yield from self.log(
                f'Agent {agent.profile.name} generated insights: {str(insights)}'
            )

            ideas = []
            idea = agent.think_idea(insights=insights, config=self.config)
            ideas.append(idea)
            yield from self.log(
                f'Agent {agent.profile.name} generated idea: {str(idea)}'
            )
            for collaborator_agent in collaborator_agents:
                idea = collaborator_agent.think_idea(
                    insights=insights, config=self.config
                )
                ideas.append(idea)
                yield from self.log(
                    f"Agent {agent.profile.name}'s collaborator {collaborator_agent.profile.name} generated ideas: {str(idea)}"
                )
            summarized_idea = agent.summarize_ideas(ideas=ideas, config=self.config)
            paper: ResearchPaperSubmission = agent.write_paper(
                idea=summarized_idea, papers=papers, config=self.config
            )
            yield from self.log(f'Agent {agent.profile.name} wrote paper: {str(paper)}')
            yield from self.log(f'Agent {agent.profile.name} started paper submission')

            if agent.profile.name is not None:
                submissions[agent.profile.name] = paper
        self.db.update(cls=ResearchPaperSubmission, conditions={}, updates=submissions)
        self.submit_paper(submissions)
        yield from self.log('PaperSubmissionMultiAgentEnvironment completed')

    @beartype
    def submit_paper(self, paper_dict: Dict[str, ResearchPaperSubmission]) -> None:
        for _, paper in paper_dict.items():
            self.paper = PaperProfile(title=paper.title, abstract=paper.abstract)
            break
