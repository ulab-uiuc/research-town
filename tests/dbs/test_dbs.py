import json
import pickle
import shutil
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

import torch
from beartype.typing import Any, Dict, List

from research_town.dbs import (
    Idea,
    LogDB,
    MetaReviewWritingLog,
    Paper,
    PaperDB,
    Profile,
    ProfileDB,
    ProgressDB,
    RebuttalWritingLog,
    ReviewWritingLog,
)
from tests.constants.config_constants import example_config
from tests.constants.data_constants import agent_profile_A, research_proposal_A
from tests.constants.db_constants import example_profile_db
from tests.mocks.mocking_func import mock_prompting


def test_LogDB_basic() -> None:
    db = LogDB()
    review_log = ReviewWritingLog(
        profile_pk='agent1',
        review_pk='review1',
    )
    rebuttal_log = RebuttalWritingLog(
        profile_pk='agent1',
        rebuttal_pk='rebuttal1',
    )
    metareview_log = MetaReviewWritingLog(
        profile_pk='agent1',
        metareview_pk='metareview1',
    )

    db.add(review_log)
    db.add(rebuttal_log)
    db.add(metareview_log)

    new_review_log = ReviewWritingLog(
        profile_pk='agent1',
        review_pk='review2',
    )
    db.add(new_review_log)
    assert new_review_log.pk in db.dbs['ReviewWritingLog'].data
    assert len(db.dbs['ReviewWritingLog'].data) == 2

    conditions: Dict[str, Any] = {'profile_pk': 'agent1'}
    results = db.get(ReviewWritingLog, **conditions)
    assert len(results) == 2

    updates = {'review_pk': 'review2'}
    updated_conditions = {'profile_pk': 'agent1'}
    updated_count = db.update(ReviewWritingLog, updates, **updated_conditions)
    assert updated_count == 2

    updated_log = db.get(ReviewWritingLog, **conditions)[0]

    assert updated_log.review_pk == 'review2'

    delete_conditions = {'profile_pk': 'agent1'}
    deleted_count = db.delete(ReviewWritingLog, **delete_conditions)
    assert deleted_count == 2

    results = db.get(ReviewWritingLog, **conditions)
    assert len(results) == 0

    with TemporaryDirectory() as temp_dir:
        db.save_to_json(temp_dir)

        new_db = LogDB()
        new_db.load_from_json(temp_dir)

        assert len(new_db.dbs['ReviewWritingLog'].data) == 0
        assert len(new_db.dbs['RebuttalWritingLog'].data) == 1
        assert len(new_db.dbs['MetaReviewWritingLog'].data) == 1


def test_progressdb_basic() -> None:
    db = ProgressDB()
    idea1 = Idea(content='Idea for a new AI algorithm')
    idea2 = Idea(content='Quantum computing research plan')

    db.add(idea1)
    db.add(idea2)

    new_idea = Idea(content='Blockchain research proposal')
    db.add(new_idea)
    assert new_idea.pk in db.dbs['Idea'].data

    content: Dict[str, Any] = {'content': 'Idea for a new AI algorithm'}
    results = db.get(Idea, **content)
    assert len(results) == 1
    assert results[0].content == 'Idea for a new AI algorithm'

    updates = {'content': 'Updated idea content'}
    conditions = {'content': 'Idea for a new AI algorithm'}
    updated_count = db.update(Idea, updates, **conditions)
    assert updated_count == 1
    content2: Dict[str, Any] = {'content': 'Updated idea content'}
    updated_results = db.get(Idea, **content2)
    assert len(updated_results) == 1
    assert updated_results[0].content == 'Updated idea content'

    content3: Dict[str, Any] = {'content': 'Quantum computing research plan'}
    deleted_count = db.delete(Idea, **content3)
    assert deleted_count == 1
    remaining_results = db.get(Idea, **content3)
    assert len(remaining_results) == 0

    with TemporaryDirectory() as temp_dir:
        db.save_to_json(temp_dir)

        new_db = ProgressDB()
        new_db.load_from_json(temp_dir)

        assert len(new_db.dbs['Idea'].data) == 2


def test_ProfileDB_basic() -> None:
    db = ProfileDB()
    agent1 = Profile(name='John Doe', bio='Profile in AI', institute='AI Institute')
    agent2 = Profile(name='Jane Smith', bio='Expert in NLP', institute='NLP Lab')
    db.add(agent1)
    db.add(agent2)

    agent3 = Profile(name='Alice Johnson', bio='Data Scientist', institute='Data Lab')
    db.add(agent3)
    assert agent3.pk in db.data
    assert db.data[agent3.pk].name == 'Alice Johnson'

    updates = {'bio': 'Senior Profile in AI'}
    success = db.update(agent1.pk, updates)

    assert success
    assert db.data[agent1.pk].bio == 'Senior Profile in AI'

    success = db.update('non-existing-pk', {'bio': 'New Bio'})
    assert not success

    success = db.delete(agent1.pk)
    assert success
    assert agent1.pk not in db.data

    success = db.delete('non-existing-pk')
    assert not success

    conditions: Dict[str, str] = {'name': 'Jane Smith'}

    results: List[Profile] = db.get(**conditions)

    assert len(results) == 1
    assert results[0].name == 'Jane Smith'

    with TemporaryDirectory() as temp_dir:
        db.save_to_json(temp_dir)


def test_Paperdb_basic() -> None:
    db = PaperDB()
    paper1 = Paper(
        title='Sample Paper 1',
        abstract='This is the abstract for paper 1',
        authors=['Author A', 'Author B'],
        url='http://example.com/paper1',
        timestamp=1617181723,
        keywords=['AI', 'ML'],
        domain='Computer Science',
        citation_count=10,
    )
    paper2 = Paper(
        title='Sample Paper 2',
        abstract='This is the abstract for paper 2',
        authors=['Author C'],
        url='http://example.com/paper2',
        timestamp=1617181756,
        keywords=['Quantum Computing'],
        domain='Physics',
        citation_count=5,
    )
    db.add(paper1)
    db.add(paper2)

    new_paper = Paper(
        title='Sample Paper 3',
        abstract='This is the abstract for paper 3',
        authors=['Author D'],
        url='http://example.com/paper3',
        timestamp=1617181789,
        keywords=['Blockchain'],
        domain='Computer Science',
        citation_count=2,
    )
    db.add(new_paper)
    assert new_paper.pk in db.data

    conditions = {'pk': paper1.pk}
    paper: Paper = db.get(**conditions)[0]
    assert paper is not None
    assert paper.title == 'Sample Paper 1'

    updates: Dict[str, Any] = {'title': 'Updated Sample Paper 1', 'citation_count': 15}

    result = db.update(paper1.pk, updates)
    assert result

    conditions = {'pk': paper1.pk}
    updated_paper: Paper = db.get(**conditions)[0]
    assert updated_paper is not None
    assert updated_paper.title == 'Updated Sample Paper 1'
    assert updated_paper.citation_count == 15

    result = db.delete(paper2.pk)
    assert result

    domain: Dict[str, Any] = {'domain': 'Computer Science'}
    results: List[Paper] = db.get(**domain)
    assert len(results) == 2
    assert results[0].title == 'Updated Sample Paper 1'
    assert results[1].title == 'Sample Paper 3'

    with TemporaryDirectory() as temp_dir:
        db.save_to_json(temp_dir)

        new_db = PaperDB()
        new_db.load_from_json(temp_dir)

        assert len(new_db.data) == 2
        assert paper1.pk in new_db.data
        assert new_db.data[paper1.pk].title == 'Updated Sample Paper 1'


def test_agent_match() -> None:
    db = ProfileDB()
    profile1 = Profile(name='John Doe', bio='Profile in AI', institute='AI Institute')
    profile2 = Profile(name='Jane Smith', bio='Expert in NLP', institute='NLP Lab')
    profile3 = Profile(name='Jane kid', bio='Expert in RL', institute='RL Lab')
    db.add(profile1)
    db.add(profile2)
    db.add(profile3)
    leader_profile = 'Profile in CV'
    match_profiles = db.match(query=leader_profile, num=2)
    assert match_profiles
    assert len(match_profiles) == 2


def test_paper_match() -> None:
    db = PaperDB()
    paper1 = Paper(
        title='Sample Paper 1',
        abstract='This is the abstract for paper 1',
        authors=['Author A', 'Author B'],
        url='http://example.com/paper1',
        timestamp=1617181723,
        keywords=['AI', 'ML'],
        domain='Computer Science',
        citation_count=10,
    )
    paper2 = Paper(
        title='Sample Paper 2',
        abstract='This is the abstract for paper 2',
        authors=['Author C'],
        url='http://example.com/paper2',
        timestamp=1617181756,
        keywords=['Quantum Computing'],
        domain='Physics',
        citation_count=5,
    )
    paper3 = Paper(
        title='Sample Paper 3',
        abstract='This is the abstract for paper 3',
        authors=['Author D'],
        url='http://example.com/paper3',
        timestamp=1617181789,
        keywords=['Blockchain'],
        domain='Computer Science',
        citation_count=2,
    )
    db.add(paper1)
    db.add(paper2)
    db.add(paper3)
    lead_agent_profile = 'Profile in CV'
    match_papers = db.match(query=lead_agent_profile, num=2)
    assert match_papers
    assert len(match_papers) == 2


def test_agent_file() -> None:
    db = ProfileDB()
    agent1 = Profile(name='John Doe', bio='Profile in AI', institute='AI Institute')
    agent2 = Profile(name='Jane Smith', bio='Expert in NLP', institute='NLP Lab')
    db.add(agent1)
    db.add(agent2)
    # save without embeddings
    db.save_to_json('data/test')
    with open('data/test/ProfileDB.json', 'r') as f:
        data_test = json.load(f)
    assert len(data_test) > 0
    assert db.data == {pk: Profile(**data) for pk, data in data_test.items()}
    # load without embeddings
    db_test = ProfileDB()
    db_test.load_from_json('data/test')
    assert db.data == db_test.data
    # save with embeddings
    db.transform_to_embed()
    db.save_to_json('data/test', with_embed=True)
    with open('data/test/ProfileDB.pkl', 'rb') as f:
        data_embed_test = pickle.load(f)
    assert db.data_embed.keys() == data_embed_test.keys()
    for profile_pk in db.data_embed:
        assert torch.equal(db.data_embed[profile_pk], data_embed_test[profile_pk])
    # load with embeddings
    db_test = ProfileDB()
    db_test.load_from_json('data/test', with_embed=True)
    assert db.data_embed.keys() == db_test.data_embed.keys()
    for profile_pk in db.data_embed:
        assert torch.equal(db.data_embed[profile_pk], db_test.data_embed[profile_pk])
    # delete test file
    shutil.rmtree('data/test')


def test_paper_file() -> None:
    db = PaperDB()
    paper1 = Paper(
        title='Sample Paper 1',
        abstract='This is the abstract for paper 1',
        authors=['Author A', 'Author B'],
        url='http://example.com/paper1',
        timestamp=1617181723,
        keywords=['AI', 'ML'],
        domain='Computer Science',
        citation_count=10,
    )
    paper2 = Paper(
        title='Sample Paper 2',
        abstract='This is the abstract for paper 2',
        authors=['Author C'],
        url='http://example.com/paper2',
        timestamp=1617181756,
        keywords=['Quantum Computing'],
        domain='Physics',
        citation_count=5,
    )
    db.add(paper1)
    db.add(paper2)
    # save without embeddings
    db.save_to_json('data/test')
    with open('data/test/PaperDB.json', 'r') as f:
        data_test = json.load(f)
    assert len(data_test) > 0
    assert db.data == {pk: Paper(**data) for pk, data in data_test.items()}
    # load without embeddings
    db_test = PaperDB()
    db_test.load_from_json('data/test')
    assert db.data == db_test.data
    # save with embeddings
    db.transform_to_embed()
    db.save_to_json('data/test', with_embed=True)
    with open('data/test/PaperDB.pkl', 'rb') as f:
        data_embed_test = pickle.load(f)
    assert db.data_embed.keys() == data_embed_test.keys()
    for paper_pk in db.data_embed:
        assert torch.equal(db.data_embed[paper_pk], data_embed_test[paper_pk])
    # load with embeddings
    db_test = PaperDB()
    db_test.load_from_json('data/test', with_embed=True)
    assert db.data_embed.keys() == db_test.data_embed.keys()
    for paper_pk in db.data_embed:
        assert torch.equal(db.data_embed[paper_pk], db_test.data_embed[paper_pk])
    # delete test file
    shutil.rmtree('data/test')


@patch('research_town.utils.agent_prompter.model_prompting')
def test_pull_profiles(mock_model_prompting: MagicMock) -> None:
    mock_model_prompting.side_effect = mock_prompting

    db = ProfileDB()
    agent_names = ['Jiaxuan You', 'Jure Leskovec']
    db.pull_profiles(agent_names=agent_names, config=example_config)
    assert db.data.keys()
    assert len(db.data.keys()) == 2
    assert db.data.values()


def test_pull_papers() -> None:
    db = PaperDB()
    db.pull_papers(num=2, domain='Data Mining')
    assert db.data.keys()
    assert len(db.data.keys()) == 2
    assert db.data.values()


def test_agentdb_match_member_profiles() -> None:
    example_profile_db.reset_role_availability()
    agent_profile_A.is_leader_candidate = True
    members = example_profile_db.match_member_profiles(
        leader=agent_profile_A,
        member_num=2,
    )
    assert len(members) == 2


def test_agentdb_match_reviewer_profiles() -> None:
    example_profile_db.reset_role_availability()
    agent_profile_A.is_leader_candidate = True
    reviewers = example_profile_db.match_reviewer_profiles(
        proposal=research_proposal_A,
        reviewer_num=2,
    )
    assert len(reviewers) == 2


def test_agentdb_match_chair() -> None:
    example_profile_db.reset_role_availability()
    agent_profile_A.is_leader_candidate = True
    chair = example_profile_db.match_chair_profiles(
        proposal=research_proposal_A,
        chair_num=1,
    )
    assert chair is not None
