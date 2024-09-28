import os
from tempfile import NamedTemporaryFile

import yaml

from tests.constants.config_constants import example_config


def test_default_initialization() -> None:
    config = example_config
    assert config.param.related_paper_num == 10
    assert config.param.base_llm == 'gpt-4o-mini'
    assert config.param.member_num == 3
    assert config.param.reviewer_num == 1


def test_yaml_serialization() -> None:
    config = example_config
    with NamedTemporaryFile(delete=False, suffix='.yaml') as tmpfile:
        tmpfile_path = os.path.dirname(tmpfile.name)
        config.save_all(tmpfile_path)

    for yaml_file in os.listdir(tmpfile_path):
        if yaml_file.endswith('.yaml'):
            with open(os.path.join(tmpfile_path, yaml_file), 'r') as f:
                loaded_data = yaml.safe_load(f)

            if 'config' in yaml_file:
                assert loaded_data['related_paper_num'] == 10
                assert loaded_data['base_llm'] == 'gpt-4o-mini'
                assert loaded_data['member_num'] == 1
