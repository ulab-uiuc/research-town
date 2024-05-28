from typing import Dict
from unittest.mock import MagicMock, patch

import pytest

from research_town.evaluators.quality_evaluator import IdeaQualityEvaluator, PaperQualityEvaluator

# Note(jinwei): please make sure the OPENAI API key is set for real tests with "use_mock=False".
@pytest.mark.parametrize("use_mock", [True])
def  test_evaluator_eval_idea(use_mock:bool) -> None:

    idea2eval = "The idea behind Mamba is to improve upon existing foundation models in deep learning, which typically rely on the Transformer architecture and its attention mechanism. While subquadratic-time architectures like linear attention, gated convolution, recurrent models, and structured state space models (SSMs) have been developed to address the inefficiency of Transformers on long sequences, they have not matched the performance of attention-based models in key areas such as language processing. Mamba addresses the shortcomings of these models by enabling content-based reasoning and making several key improvements: Adaptive SSM Parameters: By allowing SSM parameters to be functions of the input, Mamba effectively handles discrete modalities. This enables the model to selectively propagate or forget information along the sequence based on the current token.Parallel Recurrent Algorithm: Despite the changes preventing the use of efficient convolutions, Mamba employs a hardware-aware parallel algorithm in recurrent mode to maintain efficiency.Simplified Architecture: Mamba integrates these selective SSMs into a streamlined neural network architecture that does not rely on attention or MLP blocks."

    research_trend = "The current research trend in foundation models (FMs) involves developing large models that are pretrained on extensive datasets and then adapted for various downstream tasks. These FMs are primarily based on sequence models, which process sequences of inputs across different domains such as language, images, speech, audio, time series, and genomics. The predominant architecture for these models is the Transformer, which utilizes self-attention mechanisms. The strength of self-attention lies in its ability to handle complex data by routing information densely within a context window. However, this comes with significant limitations: difficulty in modeling outside of a finite context window and quadratic scaling with respect to window length.\n Efforts to create more efficient variants of attention have been extensive but often compromise the effectiveness that self-attention provides. As a result, no alternative has yet matched the empirical success of Transformers across various domains.Recently, structured state space models (SSMs) have emerged as a promising alternative. These models combine elements of recurrent neural networks (RNNs) and convolutional neural networks (CNNs), drawing from classical state space models. SSMs can be computed efficiently, either as recurrences or convolutions, and they scale linearly or near-linearly with sequence length. They also have mechanisms for modeling long-range dependencies, particularly excelling in benchmarks like the Long Range Arena.\nDifferent variants of SSMs have been successful in continuous signal data domains such as audio and vision. However, they have not been as effective in handling discrete and information-dense data, such as text, highlighting an area for further research and development."

    # an example of evaluation in https://chatgpt.com/share/b7435175-287f-464d-b3a7-1f553c51ec9e
    evaluator = IdeaQualityEvaluator(model_name="gpt-4o")
    input_dict = {'idea': idea2eval, 'trend': research_trend,'pk':0}
    if use_mock:
        with patch("research_town.utils.model_prompting.model_prompting", MagicMock(return_value=[
            "Overall Score=86. Dimension Scores=[9, 8, 9, 9, 8, 8, 8, 9, 8, 8]."
        ])):
            evals_output = evaluator.eval(**input_dict)
            assert evals_output.overall_score == 86,f"overall score of idea (mock) shoud be 86, but it's  {evals_output.overall_score}"
    else:
        evals_output = evaluator.eval(**input_dict)
        assert evals_output.overall_score>=0 and  evals_output.overall_score<=100,f"overall score of idea shoud be an Int between 0 and 100, but it's  {evals_output.overall_score}"


# Note(jinwei): please make sure the OPENAI API key is set for real tests with "use_mock=False".
@pytest.mark.parametrize("use_mock", [True])
def  test_evaluator_eval_paper(use_mock:bool) -> None:

    idea = "The idea behind Mamba is to improve upon existing foundation models in deep learning, which typically rely on the Transformer architecture and its attention mechanism. While subquadratic-time architectures like linear attention, gated convolution, recurrent models, and structured state space models (SSMs) have been developed to address the inefficiency of Transformers on long sequences, they have not matched the performance of attention-based models in key areas such as language processing. Mamba addresses the shortcomings of these models by enabling content-based reasoning and making several key improvements: Adaptive SSM Parameters: By allowing SSM parameters to be functions of the input, Mamba effectively handles discrete modalities. This enables the model to selectively propagate or forget information along the sequence based on the current token.Parallel Recurrent Algorithm: Despite the changes preventing the use of efficient convolutions, Mamba employs a hardware-aware parallel algorithm in recurrent mode to maintain efficiency.Simplified Architecture: Mamba integrates these selective SSMs into a streamlined neural network architecture that does not rely on attention or MLP blocks."

    paper_title = "Mamba: Linear-Time Sequence Modeling with Selective State Spaces"

    paper_abstract = "Foundation models, now powering most of the exciting applications in deep learning, are almost universally based on the Transformer architecture and its core attention module. Many subquadratic-time architectures such as linear attention, gated convolution and recurrent models, and structured state space models (SSMs) have been developed to address Transformers' computational inefficiency on long sequences, but they have not performed as well as attention on important modalities such as language. We identify that a key weakness of such models is their inability to perform content-based reasoning, and make several improvements. First, simply letting the SSM parameters be functions of the input addresses their weakness with discrete modalities, allowing the model to selectively propagate or forget information along the sequence length dimension depending on the current token. Second, even though this change prevents the use of efficient convolutions, we design a hardware-aware parallel algorithm in recurrent mode. We integrate these selective SSMs into a simplified end-to-end neural network architecture without attention or even MLP blocks (Mamba). Mamba enjoys fast inference (5X higher throughput than Transformers) and linear scaling in sequence length, and its performance improves on real data up to million-length sequences. As a general sequence model backbone, Mamba achieves state-of-the-art performance across several modalities such as language, audio, and genomics. On language modeling, our Mamba-3B model outperforms Transformers of the same size and matches Transformers twice its size, both in pretraining and downstream evaluation."

    
    paper = {'title': paper_title, 'abstract':paper_abstract}

    input_dict = {'idea': idea, 'paper': paper,'pk':0}
    evaluator = PaperQualityEvaluator(model_name="gpt-4o")
    if use_mock:
        with patch("research_town.utils.model_prompting.model_prompting", MagicMock(return_value=[
            "Overall Score=86. Dimension Scores=[9, 8, 9, 9, 8, 8, 8, 9, 8, 8]."
        ])):
            evals_output = evaluator.eval(**input_dict)
            assert evals_output.overall_score == 86,f"overall score of paper (mock) shoud be 86, but it's  {evals_output.overall_score}"
    else:
        evals_output = evaluator.eval(**input_dict)
        assert evals_output.overall_score>=0 and  evals_output.overall_score<=100,f"overall score of paper shoud be an Int between 0 and 100, but it's  {evals_output.overall_score}"
    