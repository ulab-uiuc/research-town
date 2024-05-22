from unittest.mock import MagicMock, patch

from research_town.envs.env_paper_rebuttal import (
    PaperRebuttalMultiAgentEnv,
)


@patch("research_town.utils.agent_prompting.openai_prompting")
def test_paper_rebuttal_env(mock_openai_prompting: MagicMock) -> None:
    mock_openai_prompting.return_value = [
        "Paper Rebuttal Environment."]
    env = PaperRebuttalMultiAgentEnv(agent_dict={"Jiaxuan You": "Jiaxuan You", "Rex Ying":
                                                 "Rex Ying", "Jure Leskovec": "Jure Leskovec", "Christos Faloutsos": "Christos Faloutsos"})
    env.assign_roles({"Jiaxuan You": "author", "Rex Ying": "author",
                     "Jure Leskovec": "reviewer", "Christos Faloutsos": "reviewer"})
    env.initialize_submission({"MambaOut: Do We Really Need Mamba for Vision?": "Mamba, an architecture with RNN-like token mixer of state space model (SSM), was recently introduced to address the quadratic complexity of the attention mechanism and subsequently applied to vision tasks. Nevertheless, the performance of Mamba for vision is often underwhelming when compared with convolutional and attention-based models. In this paper, we delve into the essence of Mamba, and conceptually conclude that Mamba is ideally suited for tasks with long-sequence and autoregressive characteristics. For vision tasks, as image classification does not align with either characteristic, we hypothesize that Mamba is not necessary for this task; Detection and segmentation tasks are also not autoregressive, yet they adhere to the long-sequence characteristic, so we believe it is still worthwhile to explore Mamba's potential for these tasks. To empirically verify our hypotheses, we construct a series of models named \\emph{MambaOut} through stacking Mamba blocks while removing their core token mixer, SSM. Experimental results strongly support our hypotheses. Specifically, our MambaOut model surpasses all visual Mamba models on ImageNet image classification, indicating that Mamba is indeed unnecessary for this task. As for detection and segmentation, MambaOut cannot match the performance of state-of-the-art visual Mamba models, demonstrating the potential of Mamba for long-sequence visual tasks."})
    while not env.terminated:
        env.step()
    assert isinstance(env.review, str)
    assert isinstance(env.decision, str)
    assert isinstance(env.rebuttal, str)
