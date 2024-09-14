from research_town.configs import Config
from research_town.dbs import LogDB, PaperDB, ProgressDB, Proposal
from research_town.envs import ExperimentEnv


def run_sync_experiment(
    config_file_path: str,
    save_file_path: str,
) -> None:
    config = Config(config_file_path)
    log_db = LogDB()
    progress_db = ProgressDB()
    paper_db = PaperDB()

    paper_from_gallery = Proposal(
        title='Advancing Large-Scale Spatio-Temporal Data Analytics: Techniques for Temporal-Aware Compression, In-Database Machine Learning with Graph Neural Networks, Adaptive NUMA-Aware Scheduling, and Explainable AI',
        content='This paper explores four key concepts in the context of large-scale spatio-temporal data analytics, including temporal-aware data compression, in-database machine learning with graph neural networks, adaptive NUMA-aware scheduling for massively parallel processing, and explainable AI for spatio-temporal graph neural networks. First, we introduce a novel temporal-aware compression technique that leverages temporal locality and patterns in large-scale spatio-temporal datasets, leading to more efficient storage and faster query processing. Second, we investigate the integration of graph neural networks within database management systems to enable in-database machine learning for graph-structured data, reducing data movement and improving performance. Third, we present adaptive NUMA-aware scheduling strategies for massively parallel processing systems, enabling dynamic resource allocation based on workload characteristics and NUMA architecture properties for better performance and scalability. Fourth, we focus on developing explainable AI techniques for spatio-temporal graph neural networks, providing insights into the decision-making process and improving trustworthiness and interpretability for complex urban and environmental management problems. External data from related papers highlight the potential of Large Language Models (LLMs) in automating the creation of scenario-based ontology and the introduction of a new task, Zero-Shot 3D Reasoning Segmentation, for parts searching and localization for objects. Additionally, we discuss Spatio-Spectral Graph Neural Networks , a new modeling paradigm for Graph Neural Networks (GNNs) that combines spatially and spectrally parametrized graph filters, overcoming limitations of traditional MPGNNs.',
    )

    progress_db.add(paper_from_gallery)

    exp_env = ExperimentEnv(
        paper_db=paper_db,
        progress_db=progress_db,
        log_db=log_db,
        config=config,  # set exp model name
    )

    exp_env.run(time_step=0, paper_pk=paper_from_gallery.pk)

    return


def main() -> None:
    run_sync_experiment(
        config_file_path='../configs',
        save_file_path='./research_town_demo_log',
    )


if __name__ == '__main__':
    main()
