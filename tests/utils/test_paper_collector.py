import datetime
from unittest.mock import MagicMock, patch
from xml.etree import ElementTree

import torch

from research_town.utils.paper_collector import (
    find_text,
    get_daily_papers,
    get_paper_list,
    get_papers,
    get_related_papers,
    neighborhood_search,
    select_papers,
)

ATOM_NAMESPACE = '{http://www.w3.org/2005/Atom}'


def test_get_related_papers() -> None:
    with (
        patch(
            'research_town.utils.paper_collector.get_bert_embedding'
        ) as mock_get_bert_embedding,
        patch(
            'research_town.utils.paper_collector.neighborhood_search'
        ) as mock_neighborhood_search,
    ):
        corpus = ['Paper 1', 'Paper 2', 'Paper 3']
        query = 'Interesting query'
        num = 2
        mock_get_bert_embedding.side_effect = [
            [torch.tensor([1, 2, 3]) for _ in corpus],
            [torch.tensor([1, 2, 3])],
        ]
        mock_neighborhood_search.return_value = torch.tensor([[0, 1]])

        result = get_related_papers(corpus, query, num)
        expected_result = ['Paper 1', 'Paper 2']
        assert result == expected_result


def test_neighborhood_search() -> None:
    query_data = [torch.tensor([[1.0, 2.0, 3.0]])]
    corpus_data = [torch.tensor([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])]
    num = 1
    result = neighborhood_search(query_data, corpus_data, num)
    assert result == [[0]]


def test_find_text() -> None:
    element = ElementTree.Element('root')
    child = ElementTree.SubElement(element, 'child')
    child.text = 'test text'
    result = find_text(element, 'child')
    assert result == 'test text'


def test_get_daily_papers() -> None:
    with patch('arxiv.Client') as mock_client:
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance

        mock_paper_1 = MagicMock()
        mock_paper_1.title = 'Paper 1'
        mock_paper_1.entry_id = 'http://example.com/1'
        mock_paper_1.summary = 'Summary 1'
        mock_paper_1.published = datetime.datetime(2023, 7, 1)

        mock_paper_2 = MagicMock()
        mock_paper_2.title = 'Paper 2'
        mock_paper_2.entry_id = 'http://example.com/2'
        mock_paper_2.summary = 'Summary 2'
        mock_paper_2.published = datetime.datetime(2023, 7, 2)

        mock_client_instance.results.return_value = [mock_paper_1, mock_paper_2]

        result, newest_day = get_daily_papers('test_topic')

        assert len(result) == 2
        assert newest_day == datetime.date(2023, 7, 2)  # Compare to the date part only


def test_get_papers() -> None:
    xml_str = """
    <root xmlns="http://www.w3.org/2005/Atom">
        <entry>
            <title>Test Paper 1</title>
            <published>2023-07-01T00:00:00Z</published>
            <summary>Abstract 1</summary>
            <author><name>Author 1</name></author>
            <author><name>Coauthor 1</name></author>
            <id>http://example.com/1</id>
        </entry>
        <entry>
            <title>Test Paper 2</title>
            <published>2023-07-02T00:00:00Z</published>
            <summary>Abstract 2</summary>
            <author><name>Author 2</name></author>
            <author><name>Coauthor 2</name></author>
            <id>http://example.com/2</id>
        </entry>
    </root>
    """
    root = ElementTree.fromstring(xml_str)
    entries = root.findall(f'{ATOM_NAMESPACE}entry')
    result, papers_by_year = get_papers(entries, 'Author 1')
    assert len(result) == 1
    assert len(papers_by_year) == 1


def test_select_papers() -> None:
    xml_str = """
    <root xmlns="http://www.w3.org/2005/Atom">
        <entry>
            <title>Test Paper 1</title>
            <published>2023-07-01T00:00:00Z</published>
            <summary>Abstract 1</summary>
            <author><name>Author 1</name></author>
            <author><name>Coauthor 1</name></author>
            <id>http://example.com/1</id>
        </entry>
        <entry>
            <title>Test Paper 2</title>
            <published>2023-07-02T00:00:00Z</published>
            <summary>Abstract 2</summary>
            <author><name>Author 1</name></author>
            <author><name>Coauthor 2</name></author>
            <id>http://example.com/2</id>
        </entry>
    </root>
    """
    root = ElementTree.fromstring(xml_str)
    entries = root.findall(f'{ATOM_NAMESPACE}entry')
    papers_by_year = {2023: entries}
    result = select_papers(papers_by_year, 'Author 1')
    assert len(result) == 2


def test_get_paper_list() -> None:
    with patch('research_town.utils.paper_collector.requests.get') as mock_get:
        xml_str = """
        <root xmlns="http://www.w3.org/2005/Atom">
            <entry>
                <title>Test Paper 1</title>
                <published>2023-07-01T00:00:00Z</published>
                <summary>Abstract 1</summary>
                <author><name>Author 1</name></author>
                <author><name>Coauthor 1</name></author>
                <id>http://example.com/1</id>
            </entry>
            <entry>
                <title>Test Paper 2</title>
                <published>2023-07-02T00:00:00Z</published>
                <summary>Abstract 2</summary>
                <author><name>Author 1</name></author>
                <author><name>Coauthor 2</name></author>
                <id>http://example.com/2</id>
            </entry>
        </root>
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content.decode.return_value = xml_str
        mock_get.return_value = mock_response

        result = get_paper_list('Author 1')
        assert len(result) == 2
