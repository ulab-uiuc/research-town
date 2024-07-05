from beartype import beartype
from beartype.typing import Dict, List, Literal, Tuple, Union

from ..agents.agent_base import BaseResearchAgent
from ..configs import Config
from ..dbs import (
    AgentAgentCollaborationFindingLog,
    AgentIdeaBrainstormingLog,
    AgentPaperLiteratureReviewLog,
    AgentPaperWritingLog,
    AgentProfile,
    AgentProfileDB,
    EnvLogDB,
    PaperProfile,
    PaperProfileDB,
    ProgressDB,
    ResearchPaperSubmission,
)
from .env_base import BaseMultiAgentEnv

LogType = Union[List[Dict[str, str]], None]
Role = Literal['reviewer', 'proj_leader', 'proj_participant', 'chair'] | None


class PaperSubmissionMultiAgentEnvironment(BaseMultiAgentEnv):
    def __init__(
        self,
        agent_profiles: List[AgentProfile],
        agent_roles: List[Role],
        agent_db: AgentProfileDB,
        paper_db: PaperProfileDB,
        env_db: EnvLogDB,
        progress_db: ProgressDB,
        config: Config,
    ) -> None:
        agent_profiles, agent_roles = self.filter_agents(
            agent_profiles=agent_profiles, agent_roles=agent_roles
        )
        super().__init__(agent_profiles=agent_profiles, agent_roles=agent_roles)
        self.paper = PaperProfile()
        self.agent_db = agent_db
        self.paper_db = paper_db
        self.env_db = env_db
        self.progress_db = progress_db
        self.config = config

    @beartype
    def filter_agents(
        self, agent_profiles: List[AgentProfile], agent_roles: List[Role]
    ) -> Tuple[List[AgentProfile], List[Role]]:
        assert len(agent_profiles) == len(agent_roles)
        if 'proj_leader' not in agent_roles:
            raise ValueError('At least one proj_leader is required to submit paper.')

        valid_agent_profiles: List[AgentProfile] = []
        valid_agent_roles: List[Role] = []
        for profile, role in zip(agent_profiles, agent_roles):
            if role == 'proj_leader' or role == 'proj_participant':
                valid_agent_profiles.append(profile)
                valid_agent_roles.append(role)
        return valid_agent_profiles, valid_agent_roles

    def step(
        self,
    ) -> None:
        # TODO: support retrieval from database
        # external_data = self.env_db.get(cls=PaperProfile, conditions={})
        # yield from self.log('PaperSubmissionMultiAgentEnvironment started')
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
            # yield from self.log(
            #     f'Agent {agent.profile.name} started finding collaborators'
            # )
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
                            agent_role='proj_participant',
                        )
                        collaborator_agents.append(new_agent_obj)
                        agent_names_to_objs[researcher_profile.name] = new_agent_obj
                    else:
                        collaborator_agents.append(
                            agent_names_to_objs[researcher_profile.name]
                        )
                    # yield from self.log(
                    #     f'Agent {agent.profile.name} found {researcher_profile.name} as collaborator'
                    # )
            if collaborator_agents:
                self.env_db.add(
                    AgentAgentCollaborationFindingLog(
                        agent_pk=agent.profile.pk,
                        other_agent_pks=[
                            other_agent.profile.pk
                            for other_agent in collaborator_agents
                        ],
                    )
                )

            insights = agent.review_literature(
                papers=papers,
                domains=['machine learning'],
                config=self.config,
            )
            # yield from self.log(
            #     f'Agent {agent.profile.name} generated insights: {str(insights)}'
            # )
            for insight in insights:
                self.progress_db.add(insight)
            self.env_db.add(
                AgentPaperLiteratureReviewLog(
                    paper_pks=[paper.pk for paper in papers],
                    agent_pk=agent.profile.pk,
                    insight_pks=[insight.pk for insight in insights],
                )
            )

            ideas = []
            idea = agent.brainstorm_idea(insights=insights, config=self.config)
            ideas.append(idea)
            # yield from self.log(
            #     f'Agent {agent.profile.name} generated idea: {str(idea)}'
            # )
            self.progress_db.add(idea)
            self.env_db.add(
                AgentIdeaBrainstormingLog(idea_pk=idea.pk, agent_pk=agent.profile.pk)
            )
            for collaborator_agent in collaborator_agents:
                idea = collaborator_agent.brainstorm_idea(
                    insights=insights, config=self.config
                )
                ideas.append(idea)
                # yield from self.log(
                #     f"Agent {agent.profile.name}'s collaborator {collaborator_agent.profile.name} generated ideas: {str(idea)}"
                # )
                self.progress_db.add(idea)
                self.env_db.add(
                    AgentIdeaBrainstormingLog(
                        idea_pk=idea.pk, agent_pk=collaborator_agent.profile.pk
                    )
                )
            summarized_idea = agent.discuss_idea(ideas=ideas, config=self.config)
            paper: ResearchPaperSubmission = agent.write_paper(
                idea=summarized_idea, papers=papers, config=self.config
            )
            # yield from self.log(f'Agent {agent.profile.name} wrote paper: {str(paper)}')
            self.progress_db.add(paper)
            self.env_db.add(
                AgentPaperWritingLog(paper_pk=paper.pk, agent_pk=agent.profile.pk)
            )
            # yield from self.log(f'Agent {agent.profile.name} started paper submission')

            if agent.profile.name is not None:
                submissions[agent.profile.name] = paper
        self.env_db.update(
            cls=ResearchPaperSubmission, conditions={}, updates=submissions
        )
        self.submit_paper(submissions)
        # yield from self.log('PaperSubmissionMultiAgentEnvironment completed')

        self.env_run_number = 1
        self.terminated = True

    @beartype
    def submit_paper(self, paper_dict: Dict[str, ResearchPaperSubmission]) -> None:
        for _, paper in paper_dict.items():
            self.paper = PaperProfile(title=paper.title, abstract=paper.abstract)
            break
