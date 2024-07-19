from tempfile import NamedTemporaryFile

import pytest
import yaml

from research_town.configs import Config


def test_default_initialization() -> None:
    config = Config()
    assert config.param.related_paper_num == 10
    assert config.param.base_llm == 'mistralai/Mixtral-8x7B-Instruct-v0.1'
    assert config.param.proj_participant_num == 3
    assert config.param.domain == 'computer_vision'
    assert config.param.reviewer_num == 3
    assert config.agent_prompt_template.discuss == (
        'Please continue in a conversation with other fellow researchers for me, where you will address their concerns in a scholarly way. '
        'Here are the messages from other researchers: {message}'
    )


def test_yaml_loading() -> None:
    yaml_content = """
    param:
        related_paper_num: 5
        base_llm: 'some/other-LLM'
        proj_participant_num: 2
    agent_prompt_template:
        test1: 'template1'
        test2: 'template2'
    eval_prompt_template:
        test1: 'template1'
        test2: 'template2'
    """
    with NamedTemporaryFile(delete=False, suffix='.yaml') as tmpfile:
        tmpfile.write(yaml_content.encode())
        tmpfile_path = tmpfile.name

    config = Config(yaml_config_path=tmpfile_path)
    assert config.param.related_paper_num == 5
    assert config.param.base_llm == 'some/other-LLM'
    assert config.param.proj_participant_num == 2
    assert config.agent_prompt_template.test1 == 'template1'  # type: ignore
    assert config.agent_prompt_template.test2 == 'template2'  # type: ignore
    assert config.eval_prompt_template.test1 == 'template1'  # type: ignore
    assert config.eval_prompt_template.test2 == 'template2'  # type: ignore


def test_merging_configurations() -> None:
    base_config = {
        'param': {'related_paper_num': 10, 'proj_participant_num': 10},
        'agent_prompt_template': {'test': 'template1'},
        'eval_prompt_template': {'test': 'template1'},
    }
    new_config = {
        'param': {'related_paper_num': 5},
        'agent_prompt_template': {
            'find_collaborators': 'template2 {profile_bio} {domains}'
        },
        'eval_prompt_template': {'idea_quality': 'template2 {profile_bio} {domains}'},
    }

    config = Config()
    config.merge_from_other_cfg(base_config)

    assert config.param.related_paper_num == 10
    assert config.param.proj_participant_num == 10
    assert config.agent_prompt_template.test == 'template1'  # type: ignore

    config.merge_from_other_cfg(new_config)

    assert config.param.related_paper_num == 5
    assert config.param.proj_participant_num == 10
    assert config.agent_prompt_template.test == 'template1'  # type: ignore
    assert (
        config.agent_prompt_template.find_collaborators
        == 'template2 {profile_bio} {domains}'
    )
    assert (
        config.eval_prompt_template.idea_quality == 'template2 {profile_bio} {domains}'
    )


def test_yaml_serialization() -> None:
    config = Config()
    with NamedTemporaryFile(delete=False, suffix='.yaml') as tmpfile:
        tmpfile_path = tmpfile.name
        config.save_to_yaml(tmpfile_path)

    with open(tmpfile_path, 'r') as f:
        loaded_data = yaml.safe_load(f)

    assert loaded_data['param']['related_paper_num'] == 10
    assert loaded_data['param']['base_llm'] == 'mistralai/Mixtral-8x7B-Instruct-v0.1'
    assert loaded_data['param']['proj_participant_num'] == 3


def test_placeholder_check() -> None:
    config = Config()
    config.check_agent_prompt_template_placeholder()

    config.agent_prompt_template.write_rebuttal = 'missing {test}'
    with pytest.raises(AssertionError):
        config.check_agent_prompt_template_placeholder()

    config = Config()
    config.check_eval_prompt_template_placeholder()

    config.eval_prompt_template.insight_quality = 'missing {test}'
    with pytest.raises(AssertionError):
        config.check_eval_prompt_template_placeholder()
