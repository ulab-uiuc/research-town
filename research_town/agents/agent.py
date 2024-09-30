from beartype import beartype
from beartype.typing import Dict, List, Literal

from ..configs import Config
from ..data import Idea, Insight, MetaReview, Paper, Profile, Proposal, Rebuttal, Review
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

Role = Literal['reviewer', 'leader', 'member', 'chair'] | None


class Agent(object):
    def __init__(
        self,
        profile: Profile,
        model_name: str,
        role: Role = None,
    ) -> None:
        self.profile: Profile = profile
        self.memory: Dict[str, str] = {}
        self.role: Role = role
        self.model_name: str = model_name
        self.serializer = Serializer()

    @beartype
    def assign_role(self, role: Role) -> None:
        self.role = role

    @beartype
    @member_required
    def review_literature(
        self,
        papers: List[Paper],
        contexts: List[str],
        config: Config,
    ) -> List[Insight]:
        serialized_papers = self.serializer.serialize(papers)
        serialized_profile = self.serializer.serialize(self.profile)
        insight_contents = review_literature_prompting(
            profile=serialized_profile,
            papers=serialized_papers,
            contexts=contexts,
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
    def brainstorm_idea(
        self, insights: List[Insight], papers: List[Paper], config: Config
    ) -> Idea:
        serialized_insights = self.serializer.serialize(insights)
        serialized_papers = self.serializer.serialize(papers)
        idea_content = brainstorm_idea_prompting(
            bio=self.profile.bio,
            insights=serialized_insights,
            papers=serialized_papers,
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
    def discuss_idea(
        self, ideas: List[Idea], contexts: List[str], config: Config
    ) -> Idea:
        serialized_ideas = self.serializer.serialize(ideas)
        idea_summarized = discuss_idea_prompting(
            bio=self.profile.bio,
            contexts=contexts,
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

        proposal, q5_result = write_proposal_prompting(
            idea=serialized_idea,
            papers=serialized_papers,
            model_name=self.model_name,
            prompt_template=prompt_template,
            return_num=config.param.return_num,
            max_token_num=config.param.max_token_num,
            temperature=config.param.temperature,
            top_p=config.param.top_p,
            stream=config.param.stream,
        )
        return Proposal(
            content=proposal,
            q1=q5_result.get('q1', ''),
            q2=q5_result.get('q2', ''),
            q3=q5_result.get('q3', ''),
            q4=q5_result.get('q4', ''),
            q5=q5_result.get('q5', ''),
        )

    @beartype
    @reviewer_required
    def write_review(self, proposal: Proposal, config: Config) -> Review:
        serialized_proposal = self.serializer.serialize(proposal)

        summary, strength, weakness, ethical_concerns, score = write_review_prompting(
            proposal=serialized_proposal,
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
            proposal_pk=proposal.pk,
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
        proposal: Proposal,
        reviews: List[Review],
        config: Config,
    ) -> MetaReview:
        serialized_proposal = self.serializer.serialize(proposal)
        serialized_reviews = self.serializer.serialize(reviews)

        summary, strength, weakness, ethical_concerns, decision = (
            write_metareview_prompting(
                proposal=serialized_proposal,
                reviews=serialized_reviews,
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
            proposal_pk=proposal.pk,
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
        proposal: Proposal,
        review: Review,
        config: Config,
    ) -> Rebuttal:
        serialized_proposal = self.serializer.serialize(proposal)
        serialized_review = self.serializer.serialize(review)

        rebuttal_content, q5_result = write_rebuttal_prompting(
            proposal=serialized_proposal,
            review=serialized_review,
            model_name=self.model_name,
            prompt_template=config.agent_prompt_template.write_rebuttal,
            return_num=config.param.return_num,
            max_token_num=config.param.max_token_num,
            temperature=config.param.temperature,
            top_p=config.param.top_p,
            stream=config.param.stream,
        )

        return Rebuttal(
            proposal_pk=proposal.pk,
            reviewer_pk=review.reviewer_pk,
            author_pk=self.profile.pk,
            content=rebuttal_content,
            q1=q5_result.get('q1', ''),
            q2=q5_result.get('q2', ''),
            q3=q5_result.get('q3', ''),
            q4=q5_result.get('q4', ''),
            q5=q5_result.get('q5', ''),
        )
