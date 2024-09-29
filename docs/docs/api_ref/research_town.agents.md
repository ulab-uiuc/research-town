# research_town.agents package

## Submodules

## research_town.agents.agent module

### *class* research_town.agents.agent.Agent(profile: [Profile](research_town.dbs.md#research_town.data.Profile), model_name: str, role: Literal['reviewer', 'leader', 'member', 'chair'] | None = None)

Bases: `object`

#### assign_role(role: Literal['reviewer', 'leader', 'member', 'chair'] | None) → None

#### brainstorm_idea(insights: list[[Insight](research_town.dbs.md#research_town.data.Insight)], config: [Config](research_town.configs.md#research_town.configs.config.Config)) → [Idea](research_town.dbs.md#research_town.data.Idea)

#### discuss_idea(ideas: list[[Idea](research_town.dbs.md#research_town.data.Idea)], config: [Config](research_town.configs.md#research_town.configs.config.Config)) → [Idea](research_town.dbs.md#research_town.data.Idea)

#### review_literature(papers: list[[Paper](research_town.dbs.md#research_town.data.Paper)], domains: list[str], contexts: list[str], config: [Config](research_town.configs.md#research_town.configs.config.Config)) → list[[Insight](research_town.dbs.md#research_town.data.Insight)]

#### write_metareview(proposal: [Proposal](research_town.dbs.md#research_town.data.Proposal), reviews: list[[Review](research_town.dbs.md#research_town.data.Review)], rebuttals: list[[Rebuttal](research_town.dbs.md#research_town.data.Rebuttal)], config: [Config](research_town.configs.md#research_town.configs.config.Config)) → [MetaReview](research_town.dbs.md#research_town.data.MetaReview)

#### write_proposal(idea: [Idea](research_town.dbs.md#research_town.data.Idea), papers: list[[Paper](research_town.dbs.md#research_town.data.Paper)], config: [Config](research_town.configs.md#research_town.configs.config.Config)) → [Proposal](research_town.dbs.md#research_town.data.Proposal)

#### write_rebuttal(proposal: [Proposal](research_town.dbs.md#research_town.data.Proposal), review: [Review](research_town.dbs.md#research_town.data.Review), config: [Config](research_town.configs.md#research_town.configs.config.Config)) → [Rebuttal](research_town.dbs.md#research_town.data.Rebuttal)

#### write_review(proposal: [Proposal](research_town.dbs.md#research_town.data.Proposal), config: [Config](research_town.configs.md#research_town.configs.config.Config)) → [Review](research_town.dbs.md#research_town.data.Review)

## research_town.agents.agent_manager module

### *class* research_town.agents.agent_manager.AgentManager(config: [Config](research_town.configs.md#research_town.configs.config.Config), profile_db: [ProfileDB](research_town.dbs.md#research_town.dbs.db_profile.ProfileDB))

Bases: `object`

#### create_chair(chair_profile: [Profile](research_town.dbs.md#research_town.data.Profile)) → [Agent](#research_town.agents.agent.Agent)

#### create_leader(leader_profile: [Profile](research_town.dbs.md#research_town.data.Profile)) → [Agent](#research_town.agents.agent.Agent)

#### create_member(member_profile: [Profile](research_town.dbs.md#research_town.data.Profile)) → [Agent](#research_town.agents.agent.Agent)

#### create_reviewer(reviewer_profile: [Profile](research_town.dbs.md#research_town.data.Profile)) → [Agent](#research_town.agents.agent.Agent)

#### find_chair(proposal: [Proposal](research_town.dbs.md#research_town.data.Proposal)) → [Agent](#research_town.agents.agent.Agent)

#### find_leader(task: str) → [Agent](#research_town.agents.agent.Agent)

#### find_members(profile: [Profile](research_town.dbs.md#research_town.data.Profile)) → List[[Agent](#research_town.agents.agent.Agent)]

#### find_reviewers(proposal: [Proposal](research_town.dbs.md#research_town.data.Proposal)) → List[[Agent](#research_town.agents.agent.Agent)]

## Module contents

### *class* research_town.agents.Agent(profile: [Profile](research_town.dbs.md#research_town.data.Profile), model_name: str, role: Literal['reviewer', 'leader', 'member', 'chair'] | None = None)

Bases: `object`

#### assign_role(role: Literal['reviewer', 'leader', 'member', 'chair'] | None) → None

#### brainstorm_idea(insights: list[[Insight](research_town.dbs.md#research_town.data.Insight)], config: [Config](research_town.configs.md#research_town.configs.config.Config)) → [Idea](research_town.dbs.md#research_town.data.Idea)

#### discuss_idea(ideas: list[[Idea](research_town.dbs.md#research_town.data.Idea)], config: [Config](research_town.configs.md#research_town.configs.config.Config)) → [Idea](research_town.dbs.md#research_town.data.Idea)

#### review_literature(papers: list[[Paper](research_town.dbs.md#research_town.data.Paper)], domains: list[str], contexts: list[str], config: [Config](research_town.configs.md#research_town.configs.config.Config)) → list[[Insight](research_town.dbs.md#research_town.data.Insight)]

#### write_metareview(proposal: [Proposal](research_town.dbs.md#research_town.data.Proposal), reviews: list[[Review](research_town.dbs.md#research_town.data.Review)], rebuttals: list[[Rebuttal](research_town.dbs.md#research_town.data.Rebuttal)], config: [Config](research_town.configs.md#research_town.configs.config.Config)) → [MetaReview](research_town.dbs.md#research_town.data.MetaReview)

#### write_proposal(idea: [Idea](research_town.dbs.md#research_town.data.Idea), papers: list[[Paper](research_town.dbs.md#research_town.data.Paper)], config: [Config](research_town.configs.md#research_town.configs.config.Config)) → [Proposal](research_town.dbs.md#research_town.data.Proposal)

#### write_rebuttal(proposal: [Proposal](research_town.dbs.md#research_town.data.Proposal), review: [Review](research_town.dbs.md#research_town.data.Review), config: [Config](research_town.configs.md#research_town.configs.config.Config)) → [Rebuttal](research_town.dbs.md#research_town.data.Rebuttal)

#### write_review(proposal: [Proposal](research_town.dbs.md#research_town.data.Proposal), config: [Config](research_town.configs.md#research_town.configs.config.Config)) → [Review](research_town.dbs.md#research_town.data.Review)

### *class* research_town.agents.AgentManager(config: [Config](research_town.configs.md#research_town.configs.config.Config), profile_db: [ProfileDB](research_town.dbs.md#research_town.dbs.db_profile.ProfileDB))

Bases: `object`

#### create_chair(chair_profile: [Profile](research_town.dbs.md#research_town.data.Profile)) → [Agent](#research_town.agents.agent.Agent)

#### create_leader(leader_profile: [Profile](research_town.dbs.md#research_town.data.Profile)) → [Agent](#research_town.agents.agent.Agent)

#### create_member(member_profile: [Profile](research_town.dbs.md#research_town.data.Profile)) → [Agent](#research_town.agents.agent.Agent)

#### create_reviewer(reviewer_profile: [Profile](research_town.dbs.md#research_town.data.Profile)) → [Agent](#research_town.agents.agent.Agent)

#### find_chair(proposal: [Proposal](research_town.dbs.md#research_town.data.Proposal)) → [Agent](#research_town.agents.agent.Agent)

#### find_leader(task: str) → [Agent](#research_town.agents.agent.Agent)

#### find_members(profile: [Profile](research_town.dbs.md#research_town.data.Profile)) → List[[Agent](#research_town.agents.agent.Agent)]

#### find_reviewers(proposal: [Proposal](research_town.dbs.md#research_town.data.Proposal)) → List[[Agent](#research_town.agents.agent.Agent)]
