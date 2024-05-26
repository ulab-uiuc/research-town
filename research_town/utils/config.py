from yacs.config import CfgNode as CN

# Global config object
config_file='research_town/utils/all_config.yaml'
cfg = CN()

cfg.parameters = CN()
cfg.parameters.related_paper_num=10
cfg.parameters.base_llm="mistralai/Mixtral-8x7B-Instruct-v0.1"

cfg.prompt = CN()
cfg.prompt.summarize_research_first= [
    "Given the profile of me, keywords, some recent paper titles and abstracts. Could you summarize the keywords of high level research backgrounds and trends in this field (related to my profile if possible).",
    "Here is my profile: {profile}",
    "Here are the keywords: {keywords}"
]
cfg.prompt.summarize_research_second= [
    "Given the profile of me, keywords, some recent paper titles and abstracts. Could you summarize the keywords of high level research backgrounds and trends in this field (related to my profile if possible).",
    "Here is my profile: {profile}",
    "Here are the keywords: {keywords}",
    "Here are some recent paper titles and abstracts: {papers}"
]
cfg.prompt.find_collaborators= [
    "Given the name and profile of me, could you find {max_number} collaborators for the following collaboration task?",
    "Here is my profile: {self_serialize_all}",
    "The collaboration task include: {task_serialize_all}",
    "Here are a full list of the names and profiles of potential collaborators: {collaborators_serialize_all}",
    "Generate the collaborator in a list separated by '-' for each collaborator"
]
cfg.prompt.generate_ideas=[
    "Here is a high-level summarized trend of a research field {trend}.",
    "How do you view this field? Do you have any novel ideas or insights?",
    "Please give me 3 to 5 novel ideas and insights in bullet points. Each bullet point should be concise, containing 2 or 3 sentences."
]
cfg.prompt.summarize_research_direction= [
    "Based on the list of the researcher's first person persona from different times, please write a comprehensive first person persona.",
    "Focus more on more recent personas. Be concise and clear (around 300 words).",
    "Here are the personas from different times: {personalinfo}"
]

cfg.prompt.write_paper_abstract= [
    "Please write a paper based on the following ideas and external data. To save time, you only need to write the abstract.",
    "You might use two or more of these ideas if they are related and work well together.",
    "Here are the ideas: {ideas_serialize_all}",
    "Here are the external data, which is a list of abstracts of related papers: {papers_serialize_all}"
]

cfg.prompt.review_score= [
    "Please provide a score for the following reviews. The score should be between 1 and 10, where 1 is the lowest and 10 is the highest. Only returns one number score.",
    "Here are the reviews: {paper_review}"
]


cfg.prompt.review_paper= [
    "Please give some reviews based on the following inputs and external data.",
    "You might use two or more of these titles if they are related and work well together.",
    "Here are the external data, which is a list of related papers: {papers_serialize_all}"
]

cfg.prompt.make_review_decision= [
    "Please provide a score for the following reviews. The score should be between 1 and 10, where 1 is the lowest and 10 is the highest. Only returns one number score.",
    "Here are the reviews: {paper_review}"
]

cfg.prompt.rebut_review=[
    "Please write a rebuttal for the following submission you have made to an academic conference. Here are the reviews and decisions from the reviewers. Your rebuttal should rebut the reviews to convince the reviewers to accept your submission.",
    "Here is the submission: {submission_serialize_all}",
    "Here are the reviews: {review_serialize_all}",
    "Here are the decisions: {decision_serialize_all}"
]
cfg.prompt.communicate_with_multiple_researchers= [
    "Please continue in a conversation with other fellow researchers for me, where you will address their concerns in a scholarly way.",
    "Here are the messages from other researchers: {single_round_chat_serialize_all}"
]
cfg.merge_from_file(config_file)



