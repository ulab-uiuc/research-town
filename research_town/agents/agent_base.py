from datetime import datetime

from beartype import beartype
from beartype.typing import Any, Dict, List, Tuple

from ..configs import Config
from ..dbs import (
    AgentAgentDiscussionLog,
    AgentPaperMetaReviewLog,
    AgentPaperRebuttalLog,
    AgentPaperReviewLog,
    AgentProfile,
    PaperProfile,
    ResearchIdea,
    ResearchInsight,
    ResearchPaperSubmission,
)
from ..utils.agent_prompter import (
    discuss_prompting,
    read_paper_prompting,
    review_paper_prompting,
    review_score_prompting,
    summarize_ideas_prompting,
    think_idea_prompting,
    write_meta_review_prompting,
    write_paper_prompting,
    write_rebuttal_prompting,
)
from ..utils.serializer import Serializer


class BaseResearchAgent(object):
    def __init__(self, agent_profile: AgentProfile, model_name: str) -> None:
        self.profile: AgentProfile = agent_profile
        self.memory: Dict[str, str] = {}
        self.model_name: str = model_name
        self.serializer = Serializer()


    @beartype
    def literature_review(
        self, papers: List[PaperProfile], domains: List[str], config: Config
    ) -> Tuple[List[ResearchInsight], List[int]]:
        serialized_papers = self.serializer.serialize(papers)
        serialized_profile = self.serializer.serialize(self.profile)
        insight_contents,related_papers_idx = read_paper_prompting(
            profile=serialized_profile,
            papers=serialized_papers,
            domains=domains,
            model_name=self.model_name,
            prompt_template_query=config.prompt_template.query_paper,
            prompt_template_read=config.prompt_template.read_paper,
        )
        insights: List[ResearchInsight] = []
        for content in insight_contents:
            insights.append(ResearchInsight(content=content))
        return insights,related_papers_idx

    @beartype
    def idea_brainstorming(
        self, insights: List[ResearchInsight], config: Config
    ) -> ResearchIdea:
        serialized_insights = self.serializer.serialize(insights)
        idea_content = think_idea_prompting(
            insights=serialized_insights,
            model_name=self.model_name,
            prompt_template=config.prompt_template.think_idea,
        )[0]
        return ResearchIdea(content=idea_content)

    @beartype
    def idea_discussion(
        self, ideas: List[ResearchIdea], config: Config
    ) -> ResearchIdea:
        serialized_ideas = self.serializer.serialize(ideas)
        idea_summarized = summarize_ideas_prompting(
            ideas=serialized_ideas,
            model_name=self.model_name,
            prompt_template=config.prompt_template.summarize_ideas,
        )[0]
        return ResearchIdea(content=idea_summarized)

    @beartype
    def paper_abstract_writing(
        self, idea:  List[ResearchIdea], papers: List[PaperProfile], config: Config
    ) -> ResearchPaperSubmission:
        serialized_idea = self.serializer.serialize(idea)
        serialized_papers = self.serializer.serialize(papers)
        paper_abstract = write_paper_prompting(
            idea=serialized_idea,
            papers=serialized_papers,
            model_name=self.model_name,
            prompt_template=config.prompt_template.write_paper,
        )[0]
        return ResearchPaperSubmission(abstract=paper_abstract)

    @beartype
    def write_paper_review(
        self, profile:AgentProfile,paper: ResearchPaperSubmission, config: Config
    ) -> AgentPaperReviewLog:
        serialized_paper = self.serializer.serialize(paper)
        serialized_profile=self.serializer.serialize(profile)
        paper_review = review_paper_prompting(
            profile=serialized_profile['bio'],
            paper=serialized_paper,
            model_name=self.model_name,
            prompt_template=config.prompt_template.review_paper,
        )[0]
        review_score = review_score_prompting(
            profile=serialized_profile['bio'],
            paper_review=paper_review,
            model_name=self.model_name,
            prompt_template=config.prompt_template.review_score,
        )
        return AgentPaperReviewLog(
            timestep=(int)(datetime.now().timestamp()),
            paper_pk=paper.pk,
            agent_pk=self.profile.pk,
            review_content=paper_review,
            review_score=review_score,
        )

    @beartype
    def write_paper_meta_review(
        self, paper: ResearchPaperSubmission, reviews: List[AgentPaperReviewLog],rebuttals:AgentPaperRebuttalLog, config: Config
    ) -> AgentPaperMetaReviewLog:
        serialized_paper = self.serializer.serialize(paper)
        serialized_reviews = self.serializer.serialize(reviews)
        serialized_rebuttals=self.serializer.serialize(rebuttals)

        meta_review = write_meta_review_prompting(
            paper=serialized_paper,
            reviews=serialized_reviews,
            rebuttals=serialized_rebuttals,
            model_name=self.model_name,
            prompt_template=config.prompt_template.write_meta_review,
        )
        review_decision = 'accept' in meta_review[0].lower()

        return AgentPaperMetaReviewLog(
            timestep=(int)(datetime.now().timestamp()),
            paper_pk=paper.pk,
            agent_pk=self.profile.pk,
            decision=review_decision,
            meta_review=meta_review[0],
        )

    @beartype
    def write_rebuttal(
        self, paper: ResearchPaperSubmission, review: AgentPaperReviewLog, config: Config
    ) -> AgentPaperRebuttalLog:
        serialized_paper = self.serializer.serialize(paper)
        serialized_review = self.serializer.serialize(review)

        rebuttal_content = write_rebuttal_prompting(
            paper=serialized_paper,
            review=serialized_review,
            model_name=self.model_name,
            prompt_template=config.prompt_template.write_rebuttal,
        )[0]

        return AgentPaperRebuttalLog(
            timestep=(int)(datetime.now().timestamp()),
            paper_pk=paper.pk,
            agent_pk=self.profile.pk,
            rebuttal_content=rebuttal_content,
        )

    @beartype
    def discuss(
        self, message: AgentAgentDiscussionLog, config: Config
    ) -> AgentAgentDiscussionLog:
        serialized_message = self.serializer.serialize(message)
        message_content = discuss_prompting(
            message=serialized_message,
            model_name=self.model_name,
            prompt_template=config.prompt_template.discuss,
        )[0]
        return AgentAgentDiscussionLog(
            timestep=(int)(datetime.now().timestamp()),
            agent_from_pk=message.agent_from_pk,
            agent_from_name=message.agent_from_name,
            agent_to_pk=message.agent_to_pk,
            agent_to_name=message.agent_to_name,
            message=message_content,
        )
