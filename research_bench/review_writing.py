"""
Review Writing Process Evaluation
Input:   Real-world Papers
Process: Match Reviewers to Papers with Similar Interests
         Evaluate Reviewers' Reviews using Similarity Metrics
Output:  Reviewers' Similarity Scores
"""

from typing import Any, Dict, List, Tuple

from litellm.utils import token_counter

from research_town.agents import AgentManager
from research_town.configs import Config
from research_town.data import Profile, Proposal, Review
from research_town.dbs import LogDB, PaperDB, ProfileDB, ProgressDB
from research_town.envs import ReviewWritingEnv
from research_town.utils.model_prompting import model_prompting


def write_review_research_town(
    paper_content: str,
    profiles_reviewers: List[Profile],
    ref_contents: List[str],
    config: Config,
) -> Tuple[str, str, List[int], Dict[str, Dict[str, Any]]]:
    log_db = LogDB(config=config.database)
    progress_db = ProgressDB(config=config.database)
    paper_db = PaperDB(config=config.database)
    profile_db = ProfileDB(config=config.database)
    agent_manager = AgentManager(config=config.param, profile_db=profile_db)

    env = ReviewWritingEnv(
        name='review_writing',
        log_db=log_db,
        progress_db=progress_db,
        paper_db=paper_db,
        config=config,
        agent_manager=agent_manager,
    )

    # leader_profile = profile_db.get(name=profiles[0].name)[0]
    leader_profile = profiles_reviewers[0]

    # print('leader_profile', leader_profile)
    leader = agent_manager.create_agent(leader_profile, role='leader')
    if not leader_profile:
        raise ValueError('Failed to create leader agent')

    top_k = 3

    reviewers = [
        agent_manager.create_agent(profile, role='reviewer')
        for profile in profiles_reviewers[0:top_k]
    ]

    ref_contents = [ref if ref else '' for ref in ref_contents]

    env.on_enter(
        leader=leader,
        chair=None,
        reviewers=reviewers,
        proposals=[Proposal(content=paper_content, citations=ref_contents)],
    )

    run_result = env.run()

    strength: str = ''
    weakness: str = ''
    scores: List[int] = []

    review_per_reviewer = {}

    if run_result is not None:
        for progress, agent in run_result:
            if isinstance(progress, Review):
                assert progress.score is not None
                scores.append(progress.score)
                agent_name = agent.profile.name
                assert progress.strength is not None
                assert progress.weakness is not None
                strength = progress.strength
                weakness = progress.weakness
                review_per_reviewer[agent_name] = {
                    'strength': strength,
                    'weakness': weakness,
                    'score': progress.score,
                }

    exit_status, exit_dict = env.on_exit()
    # s_meta_review = f"{exit_dict.get('metareviews', '')}"
    return strength, weakness, scores, review_per_reviewer


# Baselines
def write_review_zero_shot(
    paper_content: str, config: Config
) -> Tuple[str, str, List[int], Dict[str, Dict[str, Any]]]:
    prompt = [
        {
            'role': 'system',
            'content': (
                'You are an autonomous intelligent agent tasked to review a submission to an academic conference. You should write the strength of this paper.\n'
                'You will be provided with the following information:\n'
                'Submission - Full content of the submitted paper.\n\n'
                'You should provide the following information:\n'
                'Strength - Advantages and strengths of the submission that can improve its chances to be accepted.\n\n'
            ),
        },
        {
            'role': 'user',
            'content': (
                f'Here is the submission: {paper_content}\n\n'
                'Please evaluate the submission based on the following criteria:\n\n'
                'Clarity: Is the writing clear, structured, and terms defined?\n'
                'Baselines: Are baseline comparisons relevant, sufficient, and not excessive?\n'
                'Novelty: Is the approach innovative or distinct from prior work?\n'
                'Results: Are improvements significant, well-supported, and statistically robust?\n'
                'Limitations: Are weaknesses acknowledged and future work discussed?\n'
                'Related Work: Are key references cited and connections made?\n'
                'Technical: Are methods detailed enough for replication?\n\n'
                'Please combine both the ideas and the experiments in the submission when evaluating it.\n'
                'When commenting on the experiments, refer to the exact numbers from the experiments.\n\n'
                'Write the strength in 200 words.\n\n'
                'Please begin writing the strength of the submission. It should be 200 words long.\n\n'
                'Please write in bullet points. Do not limit yourself to the aforementioned criteria, like clarity, baselines, novelty, results, limitations, related work, and technical.\n\n'
                'You should also use your previous experience in your profile when analyzing the submission.'
            ),
        },
    ]
    response = model_prompting(
        config.param.base_llm,
        prompt,
        max_token_num=config.param.max_token_num,
        temperature=config.param.temperature,
    )[0]
    strength = response

    prompt = [
        {
            'role': 'system',
            'content': (
                'You are an autonomous intelligent agent tasked to review a submission to an academic conference. You should write the weakness of this paper.\n'
                'You will be provided with the following information:\n'
                'Submission - Full content of the submitted paper.\n\n'
                'You should provide the following information:\n'
                "Weakness - Disadvantages and drawbacks of the submission that must be improved before it can be accepted. You should notice that the abstract might not cover every detail, so you shouldn't be overly strict.\n\n"
            ),
        },
        {
            'role': 'user',
            'content': (
                f'Here is the submission: {paper_content}\n\n'
                'Please evaluate the submission based on the following criteria:\n'
                'Clarity: Is the writing clear, structured, and terms defined?\n'
                'Baselines: Are baseline comparisons relevant, sufficient, and not excessive?\n'
                'Novelty: Is the approach innovative or distinct from prior work?\n'
                'Results: Are improvements significant, well-supported, and statistically robust?\n'
                'Limitations: Are weaknesses acknowledged and future work discussed?\n'
                'Related Work: Are key references cited and connections made?\n'
                'Technical: Are methods detailed enough for replication?\n\n'
                'Please combine both the ideas and the experiments in the submission when evaluating it.\n'
                'When commenting on the experiments, refer to the exact numbers from the experiments.\n\n'
                'Write the weakness in 200 words.\n'
                'Please begin writing the weakness of the submission. It should be 200 words long.\n\n'
                'Please write in bullet points. Do not limit yourself to the aforementioned criteria, like clarity, baselines, novelty, results, limitations, related work, and technical.\n\n'
                'You should also use your previous experience in your profile when analyzing the submission.'
            ),
        },
    ]
    response = model_prompting(
        config.param.base_llm,
        prompt,
        max_token_num=config.param.max_token_num,
        temperature=config.param.temperature,
    )[0]
    weakness = response

    prompt = [
        {
            'role': 'system',
            'content': (
                'You are an autonomous intelligent agent tasked to score the following submission. You should act as a professional and fair member of that conference to score. '
                'The score should be between 1 and 10, where 1 is the lowest and 10 is the highest.\n'
                'You will be provided with the following information:\n'
                'Paper - Full content of a submission to an academic conference.\n'
                'Strengths - Strengths of the submission.\n'
                'Weakness - Weakness of the submission.\n'
                'You should provide the following information:\n'
                'Score - A score between 1 to 10 to evaluate the overall quality of the submission to an academic journal. It should be one of 1, 2, ..., 10. 1 is the lowest score while 10 is the highest score.\n\n'
                'Please evaluate the submission based on the summarized strengths and weaknesses provided. The score should be more related to weaknesses. '
                'If there is a critical weakness in the submission, you should give a lower score. If the submission has a minor weakness, you can give a higher score. '
                'If the submission has no weaknesses, you should give a high score. But the strengths should also be considered in the evaluation.\n\n'
                'You should use this format:\n'
                'Based on the given information, I would give this submission a score of [score] out of 10.\n'
                'Here [score] should be replaced with your score.'
            ),
        },
        {
            'role': 'user',
            'content': (
                f'Here is the strength of the paper: {strength}\n\n'
                f'Here is the weakness of the paper: {weakness}\n\n'
                'Please refer to the rubrics below to evaluate the submission:\n\n'
                '10/10: The submission is in 2% of all the papers. It changed my thinking on its topic, being one of the most thorough, convincing, and well-written papers I have ever read. '
                'I will fight for this paper to be accepted.\n\n'
                '8/10: The submission is among the top 10% of all the papers. It provides sufficient justification for all its arguments and claims. '
                'Some extra experimentation is needed, but they are not essential. '
                'The proposed method is very original and it can also generalize to various fields. '
                'This submission deepens the understanding of some phenomena, or lowers the bar for future research on an existing problem.\n\n'
                '6/10: The submission gives sufficient support for its major arguments or claims. '
                'However, some minor points are not well justified and need extra support, or details. '
                'The proposed method is moderately original, and it is generalizable to various fields. '
                'The submission itself is not particularly innovative, so it would not be a significant loss if it were not accepted.\n\n'
                '5/10: Some of the major arguments or claims are not sufficiently justified. '
                'There exist major weaknesses in technical, or methodological aspects. '
                'The proposed method is somewhat original, and it is generalizable to various fields. '
                'I am more on the side of rejection, but I can be convinced otherwise.\n\n'
                '3/10: The submission makes only marginal contributions to the field.\n\n'
                '1/10: The submission is not sufficiently thorough for publication. Or it is not relevant to the conference.\n\n'
                'You should not always consider the paper generally as an acceptable one. If the paper is really bad and has critical weaknesses, you should give a low score like 3. '
                'If the paper is really good and has important strengths, we encourage you to give a high score like 9.\n\n'
                'Your score is: '
            ),
        },
    ]

    response = model_prompting(
        config.param.base_llm,
        prompt,
        max_token_num=config.param.max_token_num,
        temperature=config.param.temperature,
    )[0]
    score_options = ['10', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    score = 0
    for score_option in score_options:
        if score_option in response:
            score = int(score_option)

    return strength, weakness, [score], {}


def write_review_with_only_profiles(
    paper_content: str, profiles_reviewers: List[Profile], config: Config
) -> Tuple[str, str, List[int], Dict[str, Dict[str, Any]]]:
    # bio_strs = '\n'.join([profile.bio for profile in profiles_reviewers])
    strengths: List[str] = []
    weaknesses: List[str] = []
    scores: List[int] = []

    profiles_reviewers = profiles_reviewers[:1]

    for profile in profiles_reviewers:
        bio_str = profile.bio
        token_input_count = 0
        token_output_count = 0
        prompt = [
            {
                'role': 'system',
                'content': (
                    'You are an autonomous intelligent agent tasked to review a submission to an academic conference. You should write the strength of this paper.\n'
                    'You will be provided with the following information:\n'
                    'Submission - Full content of the submitted paper.\n\n'
                    'You should provide the following information:\n'
                    'Strength - Advantages and strengths of the submission that can improve its chances to be accepted.\n\n'
                ),
            },
            {
                'role': 'user',
                'content': (
                    f'Here is your profile: {bio_str}\n\n'
                    f'Here is the submission: {paper_content}\n\n'
                    'Please evaluate the submission based on the following criteria:\n\n'
                    'Clarity: Is the writing clear, structured, and terms defined?\n'
                    'Baselines: Are baseline comparisons relevant, sufficient, and not excessive?\n'
                    'Novelty: Is the approach innovative or distinct from prior work?\n'
                    'Results: Are improvements significant, well-supported, and statistically robust?\n'
                    'Limitations: Are weaknesses acknowledged and future work discussed?\n'
                    'Related Work: Are key references cited and connections made?\n'
                    'Technical: Are methods detailed enough for replication?\n\n'
                    'Please combine both the ideas and the experiments in the submission when evaluating it.\n'
                    'When commenting on the experiments, refer to the exact numbers from the experiments.\n\n'
                    'Write the strength in 200 words.\n\n'
                    'Please begin writing the strength of the submission. It should be 200 words long.\n\n'
                    'Please write in bullet points. Do not limit yourself to the aforementioned criteria, like clarity, baselines, novelty, results, limitations, related work, and technical.\n\n'
                    'You should also use your previous experience in your profile when analyzing the submission.'
                ),
            },
        ]
        response = model_prompting(
            config.param.base_llm,
            prompt,
            max_token_num=config.param.max_token_num,
            temperature=config.param.temperature,
        )[0]
        # write prompt[0]['content'], bio_str, paper_content to json indent 4
        # import time
        # import json
        # with open(f'./{time.time()}.json', 'w') as f:
        #     json.dump({'prompt': prompt[0]['content'], 'bio': bio_str, 'prompt': prompt}, f, indent=4)
        token_input_count += token_counter(model=config.param.base_llm, messages=prompt)
        token_output_count += token_counter(model=config.param.base_llm, text=response)
        strength = response

        prompt = [
            {
                'role': 'system',
                'content': (
                    'You are an autonomous intelligent agent tasked to review a submission to an academic conference. You should write the weakness of this paper.\n'
                    'You will be provided with the following information:\n'
                    'Submission - Full content of the submitted paper.\n\n'
                    'You should provide the following information:\n'
                    "Weakness - Disadvantages and drawbacks of the submission that must be improved before it can be accepted. You should notice that the abstract might not cover every detail, so you shouldn't be overly strict.\n\n"
                ),
            },
            {
                'role': 'user',
                'content': (
                    f'Here is your profile: {bio_str}\n\n'
                    f'Here is the submission: {paper_content}\n\n'
                    'Please evaluate the submission based on the following criteria:\n\n'
                    'Clarity: Is the writing clear, structured, and terms defined?\n'
                    'Baselines: Are baseline comparisons relevant, sufficient, and not excessive?\n'
                    'Novelty: Is the approach innovative or distinct from prior work?\n'
                    'Results: Are improvements significant, well-supported, and statistically robust?\n'
                    'Limitations: Are weaknesses acknowledged and future work discussed?\n'
                    'Related Work: Are key references cited and connections made?\n'
                    'Technical: Are methods detailed enough for replication?\n\n'
                    'Please combine both the ideas and the experiments in the submission when evaluating it.\n'
                    'When commenting on the experiments, refer to the exact numbers from the experiments.\n\n'
                    'Write the weakness in 200 words.\n\n'
                    'Please begin writing the weakness of the submission. It should be 200 words long.\n\n'
                    'Please write in bullet points. Do not limit yourself to the aforementioned criteria, like clarity, baselines, novelty, results, limitations, related work, and technical.\n\n'
                    'You should also use your previous experience in your profile when analyzing the submission.'
                ),
            },
        ]
        response = model_prompting(
            config.param.base_llm,
            prompt,
            max_token_num=config.param.max_token_num,
            temperature=config.param.temperature,
        )[0]
        token_input_count += token_counter(model=config.param.base_llm, messages=prompt)
        token_output_count += token_counter(model=config.param.base_llm, text=response)
        weakness = response

        # score based on strength and weakness
        # A score between 1 to 10 to evaluate the overall quality of the submission to an academic journal. It should be one of 1, 2, ..., 10. 1 is the lowest score while 10 is the highest score.

        prompt = [
            {
                'role': 'system',
                'content': (
                    'You are an autonomous intelligent agent tasked to score the following submission. You should act as a professional and fair member of that conference to score. '
                    'The score should be between 1 and 10, where 1 is the lowest and 10 is the highest.\n'
                    'You will be provided with the following information:\n'
                    'Paper - Full content of a submission to an academic conference.\n'
                    'Strengths - Strengths of the submission.\n'
                    'Weakness - Weakness of the submission.\n'
                    'You should provide the following information:\n'
                    'Score - A score between 1 to 10 to evaluate the overall quality of the submission to an academic journal. It should be one of 1, 2, ..., 10. 1 is the lowest score while 10 is the highest score.\n\n'
                    'Please evaluate the submission based on the summarized strengths and weaknesses provided. The score should be more related to weaknesses. '
                    'If there is a critical weakness in the submission, you should give a lower score. If the submission has a minor weakness, you can give a higher score. '
                    'If the submission has no weaknesses, you should give a high score. But the strengths should also be considered in the evaluation.\n\n'
                    'You should use this format:\n'
                    'Based on the given information, I would give this submission a score of [score] out of 10.\n'
                    'Here [score] should be replaced with your score.'
                ),
            },
            {
                'role': 'user',
                'content': (
                    f'Here is your profile: {bio_str}\n\n'
                    f'Here is the strength of the paper: {strength}\n\n'
                    f'Here is the weakness of the paper: {weakness}\n\n'
                    'Please refer to the rubrics below to evaluate the submission:\n\n'
                    '10/10: The submission is in 2% of all the papers. It changed my thinking on its topic, being one of the most thorough, convincing, and well-written papers I have ever read. '
                    'I will fight for this paper to be accepted.\n\n'
                    '8/10: The submission is among the top 10% of all the papers. It provides sufficient justification for all its arguments and claims. '
                    'Some extra experimentation is needed, but they are not essential. '
                    'The proposed method is very original and it can also generalize to various fields. '
                    'This submission deepens the understanding of some phenomena, or lowers the bar for future research on an existing problem.\n\n'
                    '6/10: The submission gives sufficient support for its major arguments or claims. '
                    'However, some minor points are not well justified and need extra support, or details. '
                    'The proposed method is moderately original, and it is generalizable to various fields. '
                    'The submission itself is not particularly innovative, so it would not be a significant loss if it were not accepted.\n\n'
                    '5/10: Some of the major arguments or claims are not sufficiently justified. '
                    'There exist major weaknesses in technical, or methodological aspects. '
                    'The proposed method is somewhat original, and it is generalizable to various fields. '
                    'I am more on the side of rejection, but I can be convinced otherwise.\n\n'
                    '3/10: The submission makes only marginal contributions to the field.\n\n'
                    '1/10: The submission is not sufficiently thorough for publication. Or it is not relevant to the conference.\n\n'
                    'You should not always consider the paper generally as an acceptable one. If the paper is really bad and has critical weaknesses, you should give a low score like 3. '
                    'If the paper is really good and has important strengths, we encourage you to give a high score like 9.\n\n'
                    'Your score is: '
                ),
            },
        ]
        response = model_prompting(
            config.param.base_llm,
            prompt,
            max_token_num=config.param.max_token_num,
            temperature=config.param.temperature,
        )[0]
        token_input_count += token_counter(model=config.param.base_llm, messages=prompt)
        token_output_count += token_counter(model=config.param.base_llm, text=response)
        score_raw = response

        score_options = ['10', '1', '2', '3', '4', '5', '6', '7', '8', '9']

        score = 0
        for score_option in score_options:
            if score_option in score_raw:
                score = int(score_option)

        strengths.append(strength)
        weaknesses.append(weakness)
        scores.append(int(score))

        print('token_input_count', token_input_count)
        print('token_output_count', token_output_count)

    token_input_count = 0
    token_output_count = 0
    # seralize reviews
    reviews_str = ''
    for score, strength, weakness in zip(scores, strengths, weaknesses):
        reviews_str += f'Score: {score}\nStrength: {strength}\nWeakness: {weakness}\n\n'

    # combine strengths, weaknesses, and scores
    prompt = [
        {
            'role': 'system',
            'content': (
                'You are an autonomous intelligent agent tasked to write the strength of the submission for the following submission you have made to an academic conference. '
                'Your summary of strength should summarize the reviews to help the reviewers to make a decision.\n'
                'You will be provided with the following information:\n'
                'Submission - Full content of the paper submitted to this conference.\n'
                'Reviews - It typically contains the score, strength, and weakness of the submission, each by a different reviewer.\n\n'
                'You should provide the following information:\n'
                'Strength - The strength of the submission based on the reviews.\n'
            ),
        },
        {
            'role': 'user',
            'content': (
                'Here are the reviews: \n'
                f'{reviews_str}\n'
                'Please summarize the important points from the "strength" section of the reviews.\n'
                'Please write in bullet points. It should be 200 words long.\n'
            ),
        },
    ]
    response = model_prompting(
        config.param.base_llm,
        prompt,
        max_token_num=config.param.max_token_num,
        temperature=config.param.temperature,
    )[0]
    token_input_count += token_counter(model=config.param.base_llm, messages=prompt)
    token_output_count += token_counter(model=config.param.base_llm, text=response)
    strength = response

    prompt = [
        {
            'role': 'system',
            'content': (
                'You are an autonomous intelligent agent tasked to write the weakness of the submission for the following submission you have made to an academic conference. '
                'Your summary of weakness should summarize the reviews to help the reviewers to make a decision.\n'
                'You will be provided with the following information:\n'
                'Submission - Full content of the paper submitted to this conference.\n'
                'Reviews - It typically contains the score, strength, and weakness of the submission, each by a different reviewer.\n\n'
                'You should provide the following information:\n'
                'Weakness - The weakness of the submission based on the reviews.\n'
            ),
        },
        {
            'role': 'user',
            'content': (
                'Here are the reviews: \n'
                f'{reviews_str}\n'
                'Please summarize the important points from the "weakness" section of the reviews.\n'
                'Please write in bullet points. It should be 200 words long.\n'
            ),
        },
    ]
    response = model_prompting(
        config.param.base_llm,
        prompt,
        max_token_num=config.param.max_token_num,
        temperature=config.param.temperature,
    )[0]
    token_input_count += token_counter(model=config.param.base_llm, messages=prompt)
    token_output_count += token_counter(model=config.param.base_llm, text=response)
    weakness = response
    response = model_prompting(
        config.param.base_llm,
        prompt,
        max_token_num=config.param.max_token_num,
        temperature=config.param.temperature,
    )[0]
    token_input_count += token_counter(model=config.param.base_llm, messages=prompt)
    token_output_count += token_counter(model=config.param.base_llm, text=response)
    weakness = response

    print('token_input_count', token_input_count)
    print('token_output_count', token_output_count)

    return strength, weakness, scores, {}


def write_review_with_only_citations(
    paper_content: str, ref_contents: List[str], config: Config
) -> Tuple[str, str, List[int], Dict[str, Dict[str, Any]]]:
    # ref_strs = '\n'.join([ref for ref in ref_contents if ref is not None])
    # we need a better format
    # 1. Cited paper reference: [ref]
    # 2. Cited paper reference: [ref]

    ref_strs = ''
    paper_index = 0
    for ref in ref_contents:
        if ref:
            ref_strs += f'{paper_index + 1}th cited abstract: {ref}\n'
            paper_index += 1

    prompt = [
        {
            'role': 'system',
            'content': (
                'You are an autonomous intelligent agent tasked to review a submission to an academic conference. You should write the strength of this paper.\n'
                'You will be provided with the following information:\n'
                'Submission - Full content of the submitted paper.\n'
                'References - Abstracts of the cited papers.\n\n'
                'You should provide the following information:\n'
                'Strength - Advantages and strengths of the submission that can improve its chances to be accepted.\n\n'
            ),
        },
        {
            'role': 'user',
            'content': (
                f'Here is the submission: {paper_content}\n\n'
                f'Here are the abstracts of the cited papers: {ref_strs}\n\n'
                'Please evaluate the submission based on the following criteria:\n\n'
                'Clarity: Is the writing clear, structured, and terms defined?\n'
                'Baselines: Are baseline comparisons relevant, sufficient, and not excessive?\n'
                'Novelty: Is the approach innovative or distinct from prior work?\n'
                'Results: Are improvements significant, well-supported, and statistically robust?\n'
                'Limitations: Are weaknesses acknowledged and future work discussed?\n'
                'Related Work: Are key references cited and connections made?\n'
                'Technical: Are methods detailed enough for replication?\n\n'
                'Please combine both the ideas and the experiments in the submission when evaluating it.\n'
                'When commenting on the experiments, refer to the exact numbers from the experiments.\n\n'
                'Write the strength in 200 words.\n\n'
                'Please begin writing the strength of the submission. It should be 200 words long.\n\n'
                'Please write in bullet points. Do not limit yourself to the aforementioned criteria, like clarity, baselines, novelty, results, limitations, related work, and technical.\n\n'
                'You should also use your previous experience in your profile when analyzing the submission.'
            ),
        },
    ]
    response = model_prompting(
        config.param.base_llm,
        prompt,
        max_token_num=config.param.max_token_num,
        temperature=config.param.temperature,
    )[0]
    strength = response

    prompt = [
        {
            'role': 'system',
            'content': (
                'You are an autonomous intelligent agent tasked to review a submission to an academic conference. You should write the weakness of this paper.\n'
                'You will be provided with the following information:\n'
                'Submission - Full content of the submitted paper.\n'
                'References - Abstracts of the cited papers.\n\n'
                'You should provide the following information:\n'
                "Weakness - Disadvantages and drawbacks of the submission that must be improved before it can be accepted. You should notice that the abstract might not cover every detail, so you shouldn't be overly strict.\n\n"
            ),
        },
        {
            'role': 'user',
            'content': (
                f'Here is the submission: {paper_content}\n\n'
                f'Here are the abstracts of the cited papers: {ref_strs}\n\n'
                'Please evaluate the submission based on the following criteria:\n\n'
                'Clarity: Is the writing clear, structured, and terms defined?\n'
                'Baselines: Are baseline comparisons relevant, sufficient, and not excessive?\n'
                'Novelty: Is the approach innovative or distinct from prior work?\n'
                'Results: Are improvements significant, well-supported, and statistically robust?\n'
                'Limitations: Are weaknesses acknowledged and future work discussed?\n'
                'Related Work: Are key references cited and connections made?\n'
                'Technical: Are methods detailed enough for replication?\n\n'
                'Please combine both the ideas and the experiments in the submission when evaluating it.\n'
                'When commenting on the experiments, refer to the exact numbers from the experiments.\n\n'
                'Write the weakness in 200 words.\n\n'
                'Please begin writing the weakness of the submission. It should be 200 words long.\n\n'
                'Please write in bullet points. Do not limit yourself to the aforementioned criteria, like clarity, baselines, novelty, results, limitations, related work, and technical.\n\n'
                'You should also use your previous experience in your profile when analyzing the submission.'
            ),
        },
    ]
    response = model_prompting(
        config.param.base_llm,
        prompt,
        max_token_num=config.param.max_token_num,
        temperature=config.param.temperature,
    )[0]
    weakness = response

    prompt = [
        {
            'role': 'system',
            'content': (
                'You are an autonomous intelligent agent tasked to score the following submission. You should act as a professional and fair member of that conference to score. '
                'The score should be between 1 and 10, where 1 is the lowest and 10 is the highest.\n'
                'You will be provided with the following information:\n'
                'Paper - Full content of a submission to an academic conference.\n'
                'Strengths - Strengths of the submission.\n'
                'Weakness - Weakness of the submission.\n'
                'You should provide the following information:\n'
                'Score - A score between 1 to 10 to evaluate the overall quality of the submission to an academic journal. It should be one of 1, 2, ..., 10. 1 is the lowest score while 10 is the highest score.\n\n'
                'Please evaluate the submission based on the summarized strengths and weaknesses provided. The score should be more related to weaknesses. '
                'If there is a critical weakness in the submission, you should give a lower score. If the submission has a minor weakness, you can give a higher score. '
                'If the submission has no weaknesses, you should give a high score. But the strengths should also be considered in the evaluation.\n\n'
                'You should use this format:\n'
                'Based on the given information, I would give this submission a score of [score] out of 10.\n'
                'Here [score] should be replaced with your score.'
            ),
        },
        {
            'role': 'user',
            'content': (
                f'Here is the strength of the paper: {strength}\n\n'
                f'Here is the weakness of the paper: {weakness}\n\n'
                'Please refer to the rubrics below to evaluate the submission:\n\n'
                '10/10: The submission is in 2% of all the papers. It changed my thinking on its topic, being one of the most thorough, convincing, and well-written papers I have ever read. '
                'I will fight for this paper to be accepted.\n\n'
                '8/10: The submission is among the top 10% of all the papers. It provides sufficient justification for all its arguments and claims. '
                'Some extra experimentation is needed, but they are not essential. '
                'The proposed method is very original and it can also generalize to various fields. '
                'This submission deepens the understanding of some phenomena, or lowers the bar for future research on an existing problem.\n\n'
                '6/10: The submission gives sufficient support for its major arguments or claims. '
                'However, some minor points are not well justified and need extra support, or details. '
                'The proposed method is moderately original, and it is generalizable to various fields. '
                'The submission itself is not particularly innovative, so it would not be a significant loss if it were not accepted.\n\n'
                '5/10: Some of the major arguments or claims are not sufficiently justified. '
                'There exist major weaknesses in technical, or methodological aspects. '
                'The proposed method is somewhat original, and it is generalizable to various fields. '
                'I am more on the side of rejection, but I can be convinced otherwise.\n\n'
                '3/10: The submission makes only marginal contributions to the field.\n\n'
                '1/10: The submission is not sufficiently thorough for publication. Or it is not relevant to the conference.\n\n'
                'You should not always consider the paper generally as an acceptable one. If the paper is really bad and has critical weaknesses, you should give a low score like 3. '
                'If the paper is really good and has important strengths, we encourage you to give a high score like 9.\n\n'
                'Your score is: '
            ),
        },
    ]
    response = model_prompting(
        config.param.base_llm,
        prompt,
        max_token_num=config.param.max_token_num,
        temperature=config.param.temperature,
    )[0]
    score_options = ['10', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    score = 0
    for score_option in score_options:
        if score_option in response:
            score = int(score_option)

    return strength, weakness, [score], {}


def write_review(
    mode: str,
    intro: str,
    profiles: List[Profile],
    profiles_reviewers: List[Profile],
    full_content: Dict[str, Any],
    ref_contents: List[str],
    config: Config,
) -> Tuple[str, str, List[int], Dict[str, Dict[str, Any]]]:
    paper_content = ''
    for idx, section in enumerate(full_content):
        paper_content += f'{idx + 1}:\n\n'
        section_text = full_content[section]
        paper_content += section_text + '\n\n'

    if mode == 'reviewer_only':
        return write_review_with_only_profiles(
            paper_content, profiles_reviewers, config
        )
    elif mode == 'citation_only':
        return write_review_with_only_citations(paper_content, ref_contents, config)
    elif mode == 'zero_shot':
        return write_review_zero_shot(paper_content, config)
    elif mode == 'research_town':
        return write_review_research_town(
            paper_content, profiles_reviewers, ref_contents, config
        )
    else:
        raise ValueError(f'Invalid review writing mode: {mode}')
