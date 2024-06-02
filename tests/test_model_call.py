from research_town.utils.model_prompting import model_prompting


def test_openai_call() -> None:
    # supported by OPENAI_API_KEY
    prompt = (
        'Here is a high-level summarized insight of a research field Machine Learning. '
    )
    response = model_prompting('gpt-3.5-turbo', prompt, mode='TEST')
    assert response is not None
    assert len(response) > 0
    assert len(response[0]) > 0


def test_togetherai_mistral_call() -> None:
    # supported by TOGETHERAI_API_KEY
    prompt = (
        'Here is a high-level summarized insight of a research field Machine Learning. '
    )
    response = model_prompting(
        'together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1', prompt, mode='TEST'
    )
    assert response is not None
    assert len(response) > 0
    assert len(response[0]) > 0
