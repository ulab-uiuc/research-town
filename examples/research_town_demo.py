from beartype.typing import List, Literal

Role = Literal['reviewer', 'proj_leader', 'proj_participant', 'chair'] | None


def run_sync_experiment(
    agent_names: List[str],
    agent_roles: List[Role],
    config_file_path: str,
) -> None:
    # Create Environment and Agents
    # TODO: need to be implemented as engine
    return


def main() -> None:
    run_sync_experiment(
        agent_names=['Jiaxuan You', 'Jure Leskovec'],
        agent_roles=['proj_leader', 'reviewer'],
        config_file_path='./configs/default_config.yaml',
    )


if __name__ == '__main__':
    main()
