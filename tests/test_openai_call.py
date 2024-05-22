from research_town.utils.agent_prompting import openai_prompting


def test_openai_call() -> None:
    prompt = "Here is a high-level summarized trend of a research field Machine Learning. "
    response = openai_prompting("mistralai/Mixtral-8x7B-Instruct-v0.1", prompt)
    assert response is not None
    assert len(response) > 0
