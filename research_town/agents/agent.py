import re

from beartype import beartype
from beartype.typing import Dict, List, Literal, Optional

from ..configs import Config
from ..dbs import Idea, Insight, MetaReview, Paper, Profile, Proposal, Rebuttal, Review
from ..utils.agent_prompter import (
    brainstorm_idea_prompting,
    discuss_idea_prompting,
    review_literature_prompting,
    write_metareview_prompting,
    write_proposal_prompting,
    write_rebuttal_prompting,
    write_review_prompting,
)
from ..utils.role_verifier import (
    chair_required,
    leader_required,
    member_required,
    reviewer_required,
)
from ..utils.serializer import Serializer

Role = Literal['reviewer', 'leader', 'member', 'chair']


class Agent(object):
    def __init__(
        self,
        agent_profile: Profile,
        model_name: str,
        agent_role: Optional[Role] = None,
    ) -> None:
        self.profile: Profile = agent_profile
        self.memory: Dict[str, str] = {}
        self.role: Role | None = agent_role
        self.model_name: str = model_name
        self.serializer = Serializer()

    @beartype
    def assign_role(self, role: Role) -> None:
        self.role = role

    @beartype
    @member_required
    def review_literature(
        self, papers: List[Paper], domains: List[str], config: Config
    ) -> List[Insight]:
        serialized_papers = self.serializer.serialize(papers)
        serialized_profile = self.serializer.serialize(self.profile)
        insight_contents = review_literature_prompting(
            profile=serialized_profile,
            papers=serialized_papers,
            domains=domains,
            model_name=self.model_name,
            prompt_template=config.agent_prompt_template.review_literature,
            return_num=config.param.return_num,
            max_token_num=config.param.max_token_num,
            temperature=config.param.temperature,
            top_p=config.param.top_p,
            stream=config.param.stream,
        )
        insights: List[Insight] = []
        for content in insight_contents:
            insights.append(Insight(content=content))
        return insights

    @beartype
    @member_required
    def brainstorm_idea(self, insights: List[Insight], config: Config) -> Idea:
        serialized_insights = self.serializer.serialize(insights)
        idea_content = brainstorm_idea_prompting(
            insights=serialized_insights,
            model_name=self.model_name,
            prompt_template=config.agent_prompt_template.brainstorm_idea,
            return_num=config.param.return_num,
            max_token_num=config.param.max_token_num,
            temperature=config.param.temperature,
            top_p=config.param.top_p,
            stream=config.param.stream,
        )[0]
        return Idea(content=idea_content)

    @beartype
    @member_required
    def discuss_idea(self, ideas: List[Idea], config: Config) -> Idea:
        serialized_ideas = self.serializer.serialize(ideas)
        idea_summarized = discuss_idea_prompting(
            ideas=serialized_ideas,
            model_name=self.model_name,
            prompt_template=config.agent_prompt_template.discuss_idea,
            return_num=config.param.return_num,
            max_token_num=config.param.max_token_num,
            temperature=config.param.temperature,
            top_p=config.param.top_p,
            stream=config.param.stream,
        )[0]
        return Idea(content=idea_summarized)

    @beartype
    @member_required
    def write_proposal(
        self, idea: Idea, papers: List[Paper], config: Config
    ) -> Proposal:
        serialized_idea = self.serializer.serialize(idea)
        serialized_papers = self.serializer.serialize(papers)

        write_proposal_strategy = config.param.write_proposal_strategy
        if write_proposal_strategy == 'default':
            prompt_template = config.agent_prompt_template.write_proposal
        elif write_proposal_strategy == 'cot':
            prompt_template = config.agent_prompt_template.write_proposal_cot
        elif write_proposal_strategy == 'react':
            prompt_template = config.agent_prompt_template.write_proposal_react
        elif write_proposal_strategy == 'reflexion':
            prompt_template = config.agent_prompt_template.write_proposal_reflexion
        else:
            print('write_proposal_strategy not supported, will use default')
            prompt_template = config.agent_prompt_template.write_proposal

        proposal = write_proposal_prompting(
            idea=serialized_idea,
            papers=serialized_papers,
            model_name=self.model_name,
            prompt_template=prompt_template,
            return_num=config.param.return_num,
            max_token_num=config.param.max_token_num,
            temperature=config.param.temperature,
            top_p=config.param.top_p,
            stream=config.param.stream,
        )[0]
        proposal = self.prompting_parser(proposal, write_proposal_strategy)
        return Proposal(abstract=proposal)

    @beartype
    @reviewer_required
    def write_review(self, paper: Proposal, config: Config) -> Review:
        serialized_paper = self.serializer.serialize(paper)

        summary, strength, weakness, ethical_concerns, score = write_review_prompting(
            paper=serialized_paper,
            model_name=self.model_name,
            summary_prompt_template=config.agent_prompt_template.write_review_summary,
            strength_prompt_template=config.agent_prompt_template.write_review_strength,
            weakness_prompt_template=config.agent_prompt_template.write_review_weakness,
            ethical_prompt_template=config.agent_prompt_template.write_review_ethical,
            score_prompt_template=config.agent_prompt_template.write_review_score,
            return_num=config.param.return_num,
            max_token_num=config.param.max_token_num,
            temperature=config.param.temperature,
            top_p=config.param.top_p,
            stream=config.param.stream,
        )
        return Review(
            paper_pk=paper.pk,
            reviewer_pk=self.profile.pk,
            summary=summary,
            strength=strength,
            weakness=weakness,
            ethical_concerns=ethical_concerns,
            score=score,
        )

    @beartype
    @chair_required
    def write_metareview(
        self,
        paper: Proposal,
        reviews: List[Review],
        rebuttals: List[Rebuttal],
        config: Config,
    ) -> MetaReview:
        serialized_paper = self.serializer.serialize(paper)
        serialized_reviews = self.serializer.serialize(reviews)
        serialized_rebuttals = self.serializer.serialize(rebuttals)

        summary, strength, weakness, ethical_concerns, decision = (
            write_metareview_prompting(
                paper=serialized_paper,
                reviews=serialized_reviews,
                rebuttals=serialized_rebuttals,
                model_name=self.model_name,
                summary_prompt_template=config.agent_prompt_template.write_metareview_summary,
                strength_prompt_template=config.agent_prompt_template.write_metareview_strength,
                weakness_prompt_template=config.agent_prompt_template.write_metareview_weakness,
                ethical_prompt_template=config.agent_prompt_template.write_metareview_ethical,
                decision_prompt_template=config.agent_prompt_template.write_metareview_decision,
                return_num=config.param.return_num,
                max_token_num=config.param.max_token_num,
                temperature=config.param.temperature,
                top_p=config.param.top_p,
                stream=config.param.stream,
            )
        )

        return MetaReview(
            paper_pk=paper.pk,
            chair_pk=self.profile.pk,
            reviewer_pks=[review.reviewer_pk for review in reviews],
            author_pk=self.profile.pk,
            summary=summary,
            strength=strength,
            weakness=weakness,
            ethical_concerns=ethical_concerns,
            decision=decision,
        )

    @beartype
    @leader_required
    def write_rebuttal(
        self,
        paper: Proposal,
        review: Review,
        config: Config,
    ) -> Rebuttal:
        serialized_paper = self.serializer.serialize(paper)
        serialized_review = self.serializer.serialize(review)

        rebuttal_content = write_rebuttal_prompting(
            paper=serialized_paper,
            review=serialized_review,
            model_name=self.model_name,
            prompt_template=config.agent_prompt_template.write_rebuttal,
            return_num=config.param.return_num,
            max_token_num=config.param.max_token_num,
            temperature=config.param.temperature,
            top_p=config.param.top_p,
            stream=config.param.stream,
        )[0]

        return Rebuttal(
            paper_pk=paper.pk,
            reviewer_pk=review.reviewer_pk,
            author_pk=self.profile.pk,
            content=rebuttal_content,
        )

    @staticmethod
    @beartype
    def prompting_parser(proposal: str, write_proposal_strategy: str) -> str:
        if write_proposal_strategy == 'default':
            return proposal.strip()
        elif write_proposal_strategy in ['cot', 'react', 'reflexion']:
            match = re.search(r'Abstract:\s*"(.*?)"', proposal, re.DOTALL)
            if match:
                return match.group(1).strip()
        else:
            print(f'Unsupported write_proposal_strategy: {write_proposal_strategy}')
            return proposal.strip()

        print(f'Failed to extract abstract for strategy: {write_proposal_strategy}')
        return proposal.strip()
