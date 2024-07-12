from unittest.mock import MagicMock, patch

import torch
from beartype.typing import Any, Dict

from research_town.utils.retriever import get_embed, rank_topk


def test_get_embed() -> None:
    with (
        patch('transformers.BertTokenizer.from_pretrained') as mock_tokenizer,
        patch('transformers.BertModel.from_pretrained') as mock_model,
    ):
        # Mock tokenizer instance
        mock_tokenizer_instance = MagicMock()
        mock_tokenizer.return_value = mock_tokenizer_instance

        def mock_tokenize(*args: Any, **kwargs: Any) -> Dict[str, torch.Tensor]:
            return {
                'input_ids': torch.tensor([[101, 102, 103]]),  # Example token IDs
                'attention_mask': torch.tensor([[1, 1, 1]]),
            }

        mock_tokenizer_instance.side_effect = mock_tokenize

        # Mock model instance
        mock_model_instance = MagicMock()
        mock_model.return_value = mock_model_instance

        def mock_forward(*args: Any, **kwargs: Any) -> Dict[str, torch.Tensor]:
            batch_size = kwargs['input_ids'].shape[0]
            seq_length = kwargs['input_ids'].shape[1]
            hidden_size = 3  # Same as in your example
            return {
                'last_hidden_state': torch.ones((batch_size, seq_length, hidden_size))
            }

        mock_model_instance.side_effect = mock_forward

        instructions = ['Test instruction']
        result = get_embed(
            instructions,
            retriever_tokenizer=mock_tokenizer_instance,
            retriever_model=mock_model_instance,
        )

        assert isinstance(result[0], torch.Tensor)
        assert result[0].shape == (1, 3)


def test_rank_topk() -> None:
    query_data = [torch.tensor([[1.0, 2.0, 3.0]])]
    corpus_data = [torch.tensor([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])]
    num = 1
    result = rank_topk(query_data, corpus_data, num)
    assert result == [[0]]
