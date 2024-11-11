import json
import os
from typing import Any, Dict, List

import pymupdf
import pymupdf4llm
from pypdf import PdfReader

from research_bench.utils import extract_json_between_markers
from research_town.agents import AgentManager
from research_town.configs import Config
from research_town.data import Profile
from research_town.dbs import LogDB, PaperDB, ProfileDB, ProgressDB
from research_town.envs import ReviewWritingEnvPaperText
from research_town.utils.model_prompting import model_prompting

template_instructions = """
Respond in the following format:

THOUGHT:
<THOUGHT>

REVIEW JSON:
```json
<JSON>
In <THOUGHT>, first briefly discuss your intuitions and reasoning for the evaluation.
Detail your high-level arguments, necessary choices, and desired outcomes of the meta-review.
Do not make generic comments here but be specific to the paper and the provided reviews.
Treat this as the note-taking phase of your meta-review.

In <JSON>, provide the meta-review in JSON format with the following fields in the order:

"Summary": A summary of the paper content and its contributions.
"Strengths": A list of strengths of the paper.
"Weaknesses": A list of weaknesses of the paper.
"Originality": A rating from 1 to 4 (1: low, 2: medium, 3: high, 4: very high).
"Quality": A rating from 1 to 4 (1: low, 2: medium, 3: high, 4: very high).
"Clarity": A rating from 1 to 4 (1: low, 2: medium, 3: high, 4: very high).
"Significance": A rating from 1 to 4 (1: low, 2: medium, 3: high, 4: very high).
"Questions": A set of clarifying questions to be answered by the paper authors.
"Limitations": A set of limitations and potential negative societal impacts of the work.
"Ethical Concerns": A boolean value indicating whether there are ethical concerns.
"Soundness": A rating from 1 to 4 (1: poor, 2: fair, 3: good, 4: excellent).
"Presentation": A rating from 1 to 4 (1: poor, 2: fair, 3: good, 4: excellent).
"Contribution": A rating from 1 to 4 (1: poor, 2: fair, 3: good, 4: excellent).
"Overall": A rating from 1 to 10 (1: very strong reject to 10: award quality).
"Confidence": A rating from 1 to 5 (1: low, 2: medium, 3: high, 4: very high, 5: absolute).
"Decision": A decision that has to be one of the following: Accept, Reject.
For the "Decision" field, don't use Weak Accept, Borderline Accept, Borderline Reject, or Strong Reject. Instead, only use Accept or Reject.
This JSON will be automatically parsed, so ensure the format is precise.
"""

# Define the neurips_form prompt
neurips_form = (
    """
Review Form
Below is a description of the questions you will be asked on the review form for each paper and some guidelines on what to consider when answering these questions.
When writing your review, please keep in mind that after decisions have been made, reviews and meta-reviews of accepted papers and opted-in rejected papers will be made public.

Summary: Briefly summarize the paper and its contributions. This is not the place to critique the paper; the authors should generally agree with a well-written summary.
Strengths and Weaknesses: Please provide a thorough assessment of the strengths and weaknesses of the paper, touching on each of the following dimensions:
Originality: Are the tasks or methods new? Is the work a novel combination of well-known techniques? (This can be valuable!) Is it clear how this work differs from previous contributions? Is related work adequately cited
Quality: Is the submission technically sound? Are claims well supported (e.g., by theoretical analysis or experimental results)? Are the methods used appropriate? Is this a complete piece of work or work in progress? Are the authors careful and honest about evaluating both the strengths and weaknesses of their work
Clarity: Is the submission clearly written? Is it well organized? (If not, please make constructive suggestions for improving its clarity.) Does it adequately inform the reader? (Note that a superbly written paper provides enough information for an expert reader to reproduce its results.)
Significance: Are the results important? Are others (researchers or practitioners) likely to use the ideas or build on them? Does the submission address a difficult task in a better way than previous work? Does it advance the state of the art in a demonstrable way? Does it provide unique data, unique conclusions about existing data, or a unique theoretical or experimental approach?
Questions: Please list up and carefully describe any questions and suggestions for the authors. Think of the things where a response from the author can change your opinion, clarify a confusion or address a limitation. This can be very important for a productive rebuttal and discussion phase with the authors.
Limitations: Have the authors adequately addressed the limitations and potential negative societal impact of their work? If not, please include constructive suggestions for improvement.
In general, authors should be rewarded rather than punished for being up front about the limitations of their work and any potential negative societal impact. You are encouraged to think through whether any critical points are missing and provide these as feedback for the authors.
Ethical concerns: If there are ethical issues with this paper, please flag the paper for an ethics review. For guidance on when this is appropriate, please review the NeurIPS ethics guidelines.
Soundness: Please assign the paper a numerical rating on the following scale to indicate the soundness of the technical claims, experimental and research methodology and on whether the central claims of the paper are adequately supported with evidence.
4: excellent
3: good
2: fair
1: poor
Presentation: Please assign the paper a numerical rating on the following scale to indicate the quality of the presentation. This should take into account the writing style and clarity, as well as contextualization relative to prior work.
4: excellent
3: good
2: fair
1: poor
Contribution: Please assign the paper a numerical rating on the following scale to indicate the quality of the overall contribution this paper makes to the research area being studied. Are the questions being asked important? Does the paper bring a significant originality of ideas and/or execution? Are the results valuable to share with the broader NeurIPS community.
4: excellent
3: good
2: fair
1: poor
Overall: Please provide an "overall score" for this submission. Choices:
10: Award quality: Technically flawless paper with groundbreaking impact on one or more areas of AI, with exceptionally strong evaluation, reproducibility, and resources, and no unaddressed ethical considerations.
9: Very Strong Accept: Technically flawless paper with groundbreaking impact on at least one area of AI and excellent impact on multiple areas of AI, with flawless evaluation, resources, and reproducibility, and no unaddressed ethical considerations.
8: Strong Accept: Technically strong paper with, with novel ideas, excellent impact on at least one area of AI or high-to-excellent impact on multiple areas of AI, with excellent evaluation, resources, and reproducibility, and no unaddressed ethical considerations.
7: Accept: Technically solid paper, with high impact on at least one sub-area of AI or moderate-to-high impact on more than one area of AI, with good-to-excellent evaluation, resources, reproducibility, and no unaddressed ethical considerations.
6: Weak Accept: Technically solid, moderate-to-high impact paper, with no major concerns with respect to evaluation, resources, reproducibility, ethical considerations.
5: Borderline accept: Technically solid paper where reasons to accept outweigh reasons to reject, e.g., limited evaluation. Please use sparingly.
4: Borderline reject: Technically solid paper where reasons to reject, e.g., limited evaluation, outweigh reasons to accept, e.g., good evaluation. Please use sparingly.
3: Reject: For instance, a paper with technical flaws, weak evaluation, inadequate reproducibility and incompletely addressed ethical considerations.
2: Strong Reject: For instance, a paper with major technical flaws, and/or poor evaluation, limited impact, poor reproducibility and mostly unaddressed ethical considerations.
1: Very Strong Reject: For instance, a paper with trivial results or unaddressed ethical considerations
Confidence: Please provide a "confidence score" for your assessment of this submission to indicate how confident you are in your evaluation. Choices:
5: You are absolutely certain about your assessment. You are very familiar with the related work and checked the math/other details carefully.
4: You are confident in your assessment, but not absolutely certain. It is unlikely, but not impossible, that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work.
3: You are fairly confident in your assessment. It is possible that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work. Math/other details were not carefully checked.
2: You are willing to defend your assessment, but it is quite likely that you did not understand the central parts of the submission or that you are unfamiliar with some pieces of related work. Math/other details were not carefully checked.
1: Your assessment is an educated guess. The submission is not in your area or the submission was difficult to understand. Math/other details were not carefully checked.
"""
    + template_instructions
)


def load_paper(pdf_path: str, num_pages: int = 0, min_size: int = 100) -> str:
    try:
        if num_pages is None:
            text: str = pymupdf4llm.to_markdown(pdf_path)
        else:
            reader = PdfReader(pdf_path)
            min_pages = min(len(reader.pages), num_pages)
            text = pymupdf4llm.to_markdown(pdf_path, pages=list(range(min_pages)))
        if len(text) < min_size:
            raise Exception('Text too short')
    except Exception as e:
        print(f'Error with pymupdf4llm, falling back to pymupdf: {e}')
        try:
            doc = pymupdf.open(pdf_path)  # open a document
            if num_pages:
                doc = doc[:num_pages]
            text = ''
            for page in doc:  # iterate the document pages
                text = text + page.get_text()  # get plain text encoded as UTF-8
            if len(text) < min_size:
                raise Exception('Text too short')
        except Exception as e:
            print(f'Error with pymupdf, falling back to pypdf: {e}')
            reader = PdfReader(pdf_path)
            if num_pages is None:
                text = ''.join(page.extract_text() for page in reader.pages)
            else:
                text = ''.join(page.extract_text() for page in reader.pages[:num_pages])
            if len(text) < min_size:
                raise Exception('Text too short')

    return text


def load_review(path: str) -> Any:
    with open(path, 'r') as json_file:
        loaded = json.load(json_file)
    return loaded['review']


dir_path = os.path.dirname(os.path.realpath(__file__))

fewshot_papers = [
    os.path.join(dir_path, 'fewshot_examples_sakana/132_automated_relational.pdf'),
    os.path.join(dir_path, 'fewshot_examples_sakana/attention.pdf'),
    os.path.join(dir_path, 'fewshot_examples_sakana/2_carpe_diem.pdf'),
]

fewshot_reviews = [
    os.path.join(dir_path, 'fewshot_examples_sakana/132_automated_relational.json'),
    os.path.join(dir_path, 'fewshot_examples_sakana/attention.json'),
    os.path.join(dir_path, 'fewshot_examples_sakana/2_carpe_diem.json'),
]


def get_review_fewshot_examples(num_fs_examples: int = 1) -> str:
    fewshot_prompt = """
Below are some sample reviews, copied from previous machine learning conferences.
Note that while each review is formatted differently according to each reviewer's style, the reviews are well-structured and therefore easy to navigate.
"""
    for paper, review in zip(
        fewshot_papers[:num_fs_examples], fewshot_reviews[:num_fs_examples]
    ):
        txt_path = paper.replace('.pdf', '.txt')
        if os.path.exists(txt_path):
            with open(txt_path, 'r') as f:
                paper_text = f.read()
        else:
            paper_text = load_paper(paper)
        review_text = load_review(review)
        fewshot_prompt += f"""
Paper:

```
{paper_text}
```

Review:

```
{review_text}
```
"""

    return fewshot_prompt


def get_meta_review(reviews: List[str], config: Config) -> Any:
    # Define the meta-reviewer system prompt
    reviewer_count = len(reviews)
    meta_reviewer_system_prompt = f"""You are an Area Chair at a machine learning conference.
You are in charge of meta-reviewing a paper that was reviewed by {reviewer_count} reviewers.
Your job is to aggregate the reviews into a single meta-review in the same format.
Be critical and cautious in your decision, find consensus, and respect the opinion of all the reviewers."""

    # Define the template instructions

    review_text = ''
    for idx, review in enumerate(reviews):
        review_text += f"""
Review {idx + 1}/{len(reviews)}:

{review}
"""

    # Combine the base prompt
    base_prompt = neurips_form + review_text

    # Start the conversation
    conversation = []
    system_prompt = meta_reviewer_system_prompt.format(reviewer_count=len(reviews))
    conversation.append({'role': 'system', 'content': system_prompt})
    conversation.append({'role': 'user', 'content': base_prompt})

    # Get the response from the language model
    response = model_prompting(config.param.base_llm, conversation)[0]
    conversation.append({'role': 'assistant', 'content': response})

    # Extract the REVIEW JSON from the assistant's response
    final_response = conversation[-1]['content']
    final_response = extract_json_between_markers(final_response)
    return json.loads(final_response)


def write_review_sakana_ai_scientist(
    paper_text: str,
    config: Config,
    num_reflections: int = 5,
    num_fs_examples: int = 1,
    num_reviews_ensemble: int = 2,
) -> str:
    # Define the reviewer system prompt
    reviewer_system_prompt_base = (
        'You are an AI researcher who is reviewing a paper that was submitted to a prestigious ML venue.'
        ' Be critical and cautious in your decision.'
    )
    reviewer_system_prompt_neg = (
        reviewer_system_prompt_base
        + ' If a paper is bad or you are unsure, give it bad scores and reject it.'
    )

    # Include few-shot examples if specified
    if num_fs_examples > 0:
        fs_prompt = get_review_fewshot_examples(num_fs_examples)
        initial_prompt = neurips_form + fs_prompt
    else:
        initial_prompt = neurips_form

    # Add the paper text to the initial prompt
    initial_prompt += f"""
Here is the paper you are asked to review:
```
{paper_text}
```"""

    # Start the conversation
    conversation = []
    conversation.append({'role': 'system', 'content': reviewer_system_prompt_neg})
    conversation.append({'role': 'user', 'content': initial_prompt})

    # If ensemble reviews are needed
    if num_reviews_ensemble > 1:
        llm_reviews = []
        for _ in range(num_reviews_ensemble):
            response = model_prompting(config.param.base_llm, conversation)[0]
            llm_reviews.append(response)

        parsed_reviews = []
        for idx, review_ in enumerate(llm_reviews):
            try:
                parsed_reviews.append(extract_json_between_markers(review_))
            except Exception as e:
                print(f'Ensemble review {idx} failed: {e}')
        parsed_reviews = [r for r in parsed_reviews if r is not None]

        # If none of the ensemble reviews are valid, raise an error
        if not parsed_reviews:
            raise ValueError('No valid reviews generated in ensemble.')

        # Get meta-review from the ensemble
        review: Dict[str, Any] = get_meta_review(
            [json.dumps(r) for r in parsed_reviews], config
        )

        # If meta-review fails, fallback to the first valid review
        if review is None:
            review = parsed_reviews[0]

        # Replace numerical scores with the average of the ensemble
        for score, limits in [
            ('Originality', (1, 4)),
            ('Quality', (1, 4)),
            ('Clarity', (1, 4)),
            ('Significance', (1, 4)),
            ('Soundness', (1, 4)),
            ('Presentation', (1, 4)),
            ('Contribution', (1, 4)),
            ('Overall', (1, 10)),
            ('Confidence', (1, 5)),
        ]:
            scores = [
                r[score]
                for r in parsed_reviews
                if score in r and limits[1] >= r[score] >= limits[0]
            ]
            if scores:
                review[score] = int(round(sum(scores) / len(scores)))

        # Rewrite the message history with the valid one and new aggregated review
        msg_history = conversation[:-1]
        msg_history += [
            {
                'role': 'assistant',
                'content': f"""
THOUGHT:
I will start by aggregating the opinions of {num_reviews_ensemble} reviewers that I previously obtained.

REVIEW JSON:
```json
{json.dumps(review)}
```
""",
            }
        ]
    else:
        # Get the initial response from the language model
        response = model_prompting(config.param.base_llm, conversation)[0]
        conversation.append({'role': 'assistant', 'content': response})
        review = extract_json_between_markers(response)

    # Reflection loop
    for current_round in range(1, num_reflections):
        reviewer_reflection_prompt = f"""Round {current_round + 1}/{num_reflections}.
In your thoughts, first carefully consider the accuracy and soundness of the review you just created.
Include any other factors that you think are important in evaluating the paper.
Ensure the review is clear and concise, and the JSON is in the correct format.
Do not make things overly complicated.
In the next attempt, try and refine and improve your review.
Stick to the spirit of the original review unless there are glaring issues.

Respond in the same format as before:
THOUGHT:
<THOUGHT>

REVIEW JSON:

json

<JSON>
If there is nothing to improve, simply repeat the previous JSON EXACTLY after the thought and include "I am done" at the end of the thoughts but before the JSON.
ONLY INCLUDE "I am done" IF YOU ARE MAKING NO MORE CHANGES."""

        conversation.append({'role': 'user', 'content': reviewer_reflection_prompt})
        response = model_prompting(config.param.base_llm, conversation)[0]
        conversation.append({'role': 'assistant', 'content': response})

        if 'I am done' in response:
            break

        review = extract_json_between_markers(response)

    return json.dumps(review)


def write_review_researchtown(
    profiles: List[Profile], paper_text: str, config: Config
) -> str:
    log_db = LogDB(config=config.database)
    progress_db = ProgressDB(config=config.database)
    paper_db = PaperDB(config=config.database)
    profile_db = ProfileDB(config=config.database)
    agent_manager = AgentManager(config=config.param, profile_db=profile_db)

    env = ReviewWritingEnvPaperText(
        name='review_writing',
        log_db=log_db,
        progress_db=progress_db,
        paper_db=paper_db,
        config=config,
        agent_manager=agent_manager,
    )

    leader_profile = profile_db.get(name=profiles[0].name)[0]
    leader = agent_manager.create_agent(leader_profile, role='leader')

    if not leader_profile:
        raise ValueError('Failed to create leader agent')

    env.on_enter(
        paper_text=paper_text,
        leader=leader,
    )

    run_results = env.run()

    if run_results is not None:
        for progress, agent in run_results:
            pass

    exit_status, exit_dict = env.on_exit()
    metareviews = exit_dict.get('metareviews')

    if metareviews and metareviews[0]:
        return metareviews[0].summary
    else:
        raise ValueError('No metareviews generated')


def write_review(
    mode: str,
    paper_text: str,
    profiles: List[Profile],
    config: Config,
) -> str:
    if mode == 'sakana_ai_scientist':
        return write_review_sakana_ai_scientist(
            paper_text=paper_text,
            config=config,
            num_reflections=5,
            num_fs_examples=1,
            num_reviews_ensemble=1,
        )
    elif mode == 'textgnn':
        return write_review_researchtown(
            profiles=profiles,
            paper_text=paper_text,
            config=config,
        )

    else:
        raise ValueError(f'Invalid review writing mode: {mode}')
