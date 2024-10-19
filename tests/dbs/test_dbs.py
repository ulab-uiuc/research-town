from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

from beartype.typing import Any, Dict, List
from pytest import MonkeyPatch

from research_town.data import (
    Idea,
    MetaReviewWritingLog,
    Paper,
    Profile,
    RebuttalWritingLog,
    ReviewWritingLog,
)
from research_town.dbs import LogDB, PaperDB, ProfileDB, ProgressDB
from research_town.dbs.db_provider import DatabaseClientHandler
from tests.constants.config_constants import example_config
from tests.mocks.mocking_func import mock_prompting


def test_LogDB_basic(monkeypatch: MonkeyPatch) -> None:
    assert DatabaseClientHandler.__client__ is None
    temp_dir = TemporaryDirectory()
    monkeypatch.setenv('DATABASE_FOLDER_PATH', temp_dir.name)

    db = LogDB(config=example_config.database)
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
    assert db.count(ReviewWritingLog, pk=new_review_log.pk) == 1
    assert db.get(ReviewWritingLog, pk=new_review_log.pk)[0].pk == new_review_log.pk
    assert db.count(ReviewWritingLog) == 2

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

    new_db = LogDB(config=example_config.database)

    assert new_db.dbs['ReviewWritingLog'].count() == 0
    assert new_db.dbs['RebuttalWritingLog'].count() == 1
    assert new_db.dbs['MetaReviewWritingLog'].count() == 1


def test_progressdb_basic(monkeypatch: MonkeyPatch) -> None:
    assert DatabaseClientHandler.__client__ is None

    temp_dir = TemporaryDirectory()
    monkeypatch.setenv('DATABASE_FOLDER_PATH', temp_dir.name)

    db = ProgressDB(config=example_config.database)
    idea1 = Idea(content='Idea for a new AI algorithm')
    idea2 = Idea(content='Quantum computing research plan')

    db.add(idea1)
    db.add(idea2)

    new_idea = Idea(content='Blockchain research proposal')
    db.add(new_idea)
    assert db.dbs['Idea'].count() == 3
    assert db.get(Idea, pk=new_idea.pk)[0].pk == new_idea.pk

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

    new_db = ProgressDB(config=example_config.database)
    assert new_db.dbs['Idea'].count() == 2


def test_ProfileDB_basic(monkeypatch: MonkeyPatch) -> None:
    assert DatabaseClientHandler.__client__ is None

    temp_dir = TemporaryDirectory()
    monkeypatch.setenv('DATABASE_FOLDER_PATH', temp_dir.name)

    db = ProfileDB(config=example_config.database)
    agent1 = Profile(name='John Doe', bio='Profile in AI', institute='AI Institute')
    agent2 = Profile(name='Jane Smith', bio='Expert in NLP', institute='NLP Lab')
    db.add(agent1)
    db.add(agent2)

    agent3 = Profile(name='Alice Johnson', bio='Data Scientist', institute='Data Lab')
    db.add(agent3)
    assert db.count(pk=agent3.pk) == 1
    assert db.get(pk=agent3.pk)[0].name == 'Alice Johnson'

    updates = {'bio': 'Senior Profile in AI'}
    success = db.update(agent1.pk, updates)

    assert success
    assert db.get(pk=agent1.pk)[0].bio == 'Senior Profile in AI'

    success = db.update('non-existing-pk', {'bio': 'New Bio'})
    assert not success

    success = db.delete(agent1.pk)
    assert success
    assert db.count(pk=agent1.pk) == 0

    success = db.delete('non-existing-pk')
    assert not success

    conditions: Dict[str, str] = {'name': 'Jane Smith'}

    results: List[Profile] = db.get(**conditions)

    assert len(results) == 1
    assert results[0].name == 'Jane Smith'


def test_Paperdb_basic(monkeypatch: MonkeyPatch) -> None:
    assert DatabaseClientHandler.__client__ is None

    temp_dir = TemporaryDirectory()
    monkeypatch.setenv('DATABASE_FOLDER_PATH', temp_dir.name)

    db = PaperDB(config=example_config.database)
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
    assert db.count(pk=new_paper.pk) == 1

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

    new_db = PaperDB(config=example_config.database)
    assert new_db.count() == 2
    assert new_db.count(pk=paper1.pk) == 1
    assert new_db.get(pk=paper1.pk)[0].title == 'Updated Sample Paper 1'


def test_agent_match(monkeypatch: MonkeyPatch) -> None:
    temp_dir = TemporaryDirectory()
    monkeypatch.setenv('DATABASE_FOLDER_PATH', temp_dir.name)

    db = ProfileDB(config=example_config.database)
    profile1 = Profile(name='John Doe', bio='Profile in AI', institute='AI Institute')
    profile2 = Profile(name='Jane Smith', bio='Expert in NLP', institute='NLP Lab')
    profile3 = Profile(name='Jane kid', bio='Expert in RL', institute='RL Lab')
    db.add(profile1)
    db.add(profile2)
    db.add(profile3)
    leader_profile = 'Profile in CV'
    match_profiles = db.match(query=leader_profile, num=2, role='leader')
    assert match_profiles
    assert len(match_profiles) == 2


def test_paper_match(monkeypatch: MonkeyPatch) -> None:
    temp_dir = TemporaryDirectory()
    monkeypatch.setenv('DATABASE_FOLDER_PATH', temp_dir.name)

    db = PaperDB(config=example_config.database)
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
    assert db.count() == 3
    assert db.get(pk=paper1.pk)[0].title == 'Sample Paper 1'

    lead_profile = 'Profile in CV'
    match_papers = db.match(query=lead_profile, num=2)
    assert match_papers
    assert len(match_papers) == 2


@patch('research_town.utils.profile_collector.model_prompting')
def test_pull_profiles(
    mock_model_prompting: MagicMock, monkeypatch: MonkeyPatch
) -> None:
    temp_dir = TemporaryDirectory()
    monkeypatch.setenv('DATABASE_FOLDER_PATH', temp_dir.name)

    mock_model_prompting.side_effect = mock_prompting

    db = ProfileDB(config=example_config.database)
    names = ['Jiaxuan You', 'Jure Leskovec']
    db.pull_profiles(names=names, config=example_config)
    assert db.count() == 2


def test_pull_papers(monkeypatch: MonkeyPatch) -> None:
    temp_dir = TemporaryDirectory()
    monkeypatch.setenv('DATABASE_FOLDER_PATH', temp_dir.name)

    db = PaperDB(config=example_config.database)
    db.pull_papers(num=2, domain='Data Mining')
    assert db.count() == 2
