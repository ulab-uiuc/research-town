import datetime
from unittest.mock import MagicMock, patch

import torch

from research_town.utils.paper_collector import get_daily_papers, get_related_papers


def test_get_related_papers() -> None:
    with (
        patch(
            'research_town.utils.paper_collector.get_embedding'
        ) as mock_get_embedding,
        patch('research_town.utils.paper_collector.rank_topk') as mock_rank_topk,
    ):
        corpus = ['Paper 1', 'Paper 2', 'Paper 3']
        query = 'Interesting query'
        num = 2
        mock_get_embedding.side_effect = [
            [torch.tensor([1, 2, 3]) for _ in corpus],
            [torch.tensor([1, 2, 3])],
        ]
        mock_rank_topk.return_value = torch.tensor([[0, 1]])

        result = get_related_papers(corpus, query, num)
        expected_result = ['Paper 1', 'Paper 2']
        assert result == expected_result


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
