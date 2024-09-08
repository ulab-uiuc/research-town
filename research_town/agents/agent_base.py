import re

from beartype import beartype
from beartype.typing import Dict, List, Literal, Optional

from ..configs import Config
from ..dbs import (
    AgentProfile,
    PaperProfile,
    ResearchIdea,
    ResearchInsight,
    ResearchMetaReview,
    ResearchPaperSubmission,
    ResearchRebuttal,
    ResearchReview,
)
from ..utils.agent_prompter import (
    brainstorm_idea_prompting,
    discuss_idea_prompting,
    review_literature_prompting,
    write_meta_review_prompting,
    write_proposal_prompting,
    write_rebuttal_prompting,
    write_review_prompting,
)
from ..utils.role_verifier import (
    chair_required,
    proj_leader_required,
    proj_participant_required,
    reviewer_required,
)
from ..utils.serializer import Serializer

Role = Literal['reviewer', 'proj_leader', 'proj_participant', 'chair']


class BaseResearchAgent(object):
    def __init__(
        self,
        agent_profile: AgentProfile,
        model_name: str,
        agent_role: Optional[Role] = None,
    ) -> None:
        self.profile: AgentProfile = agent_profile
        self.memory: Dict[str, str] = {}
        self.role: Role | None = agent_role
        self.model_name: str = model_name
        self.serializer = Serializer()

    @beartype
    def assign_role(self, role: Role) -> None:
        self.role = role

    @beartype
    @proj_participant_required
    def review_literature(
        self, papers: List[PaperProfile], domains: List[str], config: Config
    ) -> List[ResearchInsight]:
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
        insights: List[ResearchInsight] = []
        for content in insight_contents:
            insights.append(ResearchInsight(content=content))
        return insights

    @beartype
    @proj_participant_required
    def brainstorm_idea(
        self, insights: List[ResearchInsight], config: Config
    ) -> ResearchIdea:
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
        return ResearchIdea(content=idea_content)

    @beartype
    @proj_participant_required
    def discuss_idea(self, ideas: List[ResearchIdea], config: Config) -> ResearchIdea:
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
        return ResearchIdea(content=idea_summarized)
    
    @staticmethod
    @beartype
    def prompting_parser(paper_abstract: str, write_proposal_strategy: str) -> str:
        if write_proposal_strategy == 'default':
            return paper_abstract.strip()
        elif write_proposal_strategy in ['cot', 'react', 'reflexion']:
            match = re.search(r'Abstract:\s*"(.*?)"', paper_abstract, re.DOTALL)
            if match:
                return match.group(1).strip()
        else:
            print(f"Unsupported write_proposal_strategy: {write_proposal_strategy}")
            return paper_abstract.strip()

        print(f"Failed to extract abstract for strategy: {write_proposal_strategy}")
        return paper_abstract.strip()

    @beartype
    @proj_leader_required
    def write_proposal(
        self, idea: ResearchIdea, papers: List[PaperProfile], config: Config
    ) -> ResearchPaperSubmission:
        serialized_idea = self.serializer.serialize(idea)
        serialized_papers = self.serializer.serialize(papers)
        
        write_proposal_strategy = config.param.write_proposal_strategy
        if write_proposal_strategy == 'default':
            prompt_template=config.agent_prompt_template.write_proposal
        elif write_proposal_strategy == 'cot':
            prompt_template=config.agent_prompt_template.write_proposal_cot
        elif write_proposal_strategy == 'react':
            prompt_template=config.agent_prompt_template.write_proposal_react
        elif write_proposal_strategy == 'reflexion':
            prompt_template=config.agent_prompt_template.write_proposal_reflexion
        else:
            print('write_proposal_strategy not supported, will use default')
            prompt_template=config.agent_prompt_template.write_proposal

        paper_abstract = write_proposal_prompting(
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
        paper_abstract = self.prompting_parser(paper_abstract, write_proposal_strategy)
        return ResearchPaperSubmission(abstract=paper_abstract)

    @beartype
    @reviewer_required
    def write_review(
        self, paper: ResearchPaperSubmission, config: Config
    ) -> ResearchReview:
        serialized_paper = self.serializer.serialize(paper)

        summary, strength, weakness, score = write_review_prompting(
            paper=serialized_paper,
            model_name=self.model_name,
            summary_prompt_template=config.agent_prompt_template.write_review_summary,
            strength_prompt_template=config.agent_prompt_template.write_review_strength,
            weakness_prompt_template=config.agent_prompt_template.write_review_weakness,
            score_prompt_template=config.agent_prompt_template.write_review_score,
            return_num=config.param.return_num,
            max_token_num=config.param.max_token_num,
            temperature=config.param.temperature,
            top_p=config.param.top_p,
            stream=config.param.stream,
        )
        return ResearchReview(
            paper_pk=paper.pk,
            reviewer_pk=self.profile.pk,
            summary=summary,
            strength=strength,
            weakness=weakness,
            score=score,
        )

    @beartype
    @chair_required
    def write_meta_review(
        self,
        paper: ResearchPaperSubmission,
        reviews: List[ResearchReview],
        rebuttals: List[ResearchRebuttal],
        config: Config,
    ) -> ResearchMetaReview:
        serialized_paper = self.serializer.serialize(paper)
        serialized_reviews = self.serializer.serialize(reviews)
        serialized_rebuttals = self.serializer.serialize(rebuttals)

        summary, strength, weakness, decision = write_meta_review_prompting(
            paper=serialized_paper,
            reviews=serialized_reviews,
            rebuttals=serialized_rebuttals,
            model_name=self.model_name,
            summary_prompt_template=config.agent_prompt_template.write_meta_review_summary,
            strength_prompt_template=config.agent_prompt_template.write_meta_review_strength,
            weakness_prompt_template=config.agent_prompt_template.write_meta_review_weakness,
            decision_prompt_template=config.agent_prompt_template.write_meta_review_decision,
            return_num=config.param.return_num,
            max_token_num=config.param.max_token_num,
            temperature=config.param.temperature,
            top_p=config.param.top_p,
            stream=config.param.stream,
        )

        return ResearchMetaReview(
            paper_pk=paper.pk,
            chair_pk=self.profile.pk,
            reviewer_pks=[review.reviewer_pk for review in reviews],
            author_pk=self.profile.pk,
            summary=summary,
            strength=strength,
            weakness=weakness,
            decision=decision,
        )

    @beartype
    @proj_leader_required
    def write_rebuttal(
        self,
        paper: ResearchPaperSubmission,
        review: ResearchReview,
        config: Config,
    ) -> ResearchRebuttal:
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

        return ResearchRebuttal(
            paper_pk=paper.pk,
            reviewer_pk=review.reviewer_pk,
            author_pk=self.profile.pk,
            content=rebuttal_content,
        )
