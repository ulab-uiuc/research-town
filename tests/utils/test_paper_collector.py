import datetime
from unittest.mock import MagicMock, patch

from research_town.utils.paper_collector import (
    get_daily_papers,
    get_intro,
    get_paper_content,
)


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


def test_get_paper_content() -> None:
    section_contents, table_captions, figure_captions, bibliography = get_paper_content(
        'https://arxiv.org/html/2403.05534v1'
    )
    assert section_contents is not None
    assert '1 Introduction' in section_contents
    assert len(section_contents['1 Introduction']) > 0
    assert table_captions is None
    assert figure_captions is not None
    assert 'Figure 1: ' in figure_captions
    assert len(figure_captions['Figure 1: ']) > 0
    assert bibliography is not None
    assert 'Arora and Huber (2001)' in bibliography
    assert len(bibliography['Arora and Huber (2001)']) > 0


def test_get_intro() -> None:
    test_url1 = 'https://arxiv.org/pdf/2409.16928'
    test_url2 = 'https://openreview.net/pdf?id=NnMEadcdyD'
    test_url3 = 'https://arxiv.org/abs/2409.17012'
    intro1 = get_intro(test_url1)
    intro2 = get_intro(test_url2)
    intro3 = get_intro(test_url3)
    assert (
        intro1
        == '\n\n1 Introduction\n\nIn natural language processing, the two main challenges in developing new models are the difficulty in acquiring high-quality data and the extensive training times required to make models more expressive[1].\n\n\nThis work focuses on the latter issue. We experiment with unconventional computing architectures, the goal being to assess if and how they can help accelerate training time to obtain more expressive models. To this purpose, our choice is architectures that develop Adiabatic Quantum Computing (AQC), where the technology proposed by D-Wave is considered a standard. The reason is twofold. On one side AQC by its very nature solves minimization problems in the QUBO form (Quadratic Unconstrained Binary Optimization). On the other, the core of many AI problems is minimizing some functions by looking for the values of specific parameters.\n\n\nWe choose SVM[2] over more standard Transformers models because preliminary investigations on SVMs that leverage AQC already exist[3] and SVM share some similarities with the attention mechanism of Transformers[4].\n\n\nPrecalling that, among classification tasks in natural language processing, the binary version of Sentiment Analysis (BSA) aims to separate sentences that convey “positive” emotions from those that convey “negative” emotions. We reduced the BSA to QUBO and evaluated the following:\n\n\n1) performance during classification;\n\n2) the time required to train the model;\n\n3) the time required to classify new examples,\n\n\ncompared to more standard techniques implemented with heuristics and classical architectures.\nTo overcome the limited use of the quantum process unit (QPU) by the D-Wave hybrid solver, we also started to investigate algebraic-based alternatives to the proprietary mechanisms that split QUBO problems between QPU and CPU.\n\n'
    )
    assert (
        intro2
        == 'Introduction\nDiffusion-based generative models, or diffusion models in short, were ﬁrst introduced by Sohl-\nDickstein et al. [2015]. After years of relative obscurity, this class of models suddenly rose to\nprominence with the work of Song and Ermon [2019] and Ho et al. [2020] who demonstrated that,\nwith further reﬁnements in model architectures and objective functions, diffusion models can perform\nstate-of-the-art image generation.\n37th Conference on Neural Information Processing Systems (NeurIPS 2023).\n(a) 512\x02512\n (b) 256\x02256\n (c) 128\x02128\nFigure 1: Samples generated from our VDM++ diffusion models trained on the ImageNet dataset;\nsee Section 5 for details and'
    )
    assert (
        intro3
        == '\n\n1 Introduction\n\nIn recent years, Low Earth Orbit (LEO) has become increasingly crowded with debris originating from spacecraft fragmentation at the end of their operational life cycle. Collisions of such debris with space assets can often lead to catastrophic failure. One example is the Cosmos 2251-Iridium 33, which led to the destruction of the Iridium 33 satellite and added more than 2000 pieces of debris to LEO [nicholas2009collision]. In addition, collisions between objects generate new space debris, increasing the likelihood of further collisions, in what is known as the Kessler effect [kessler2010kessler_syndrome]. Although international post-mission disposal policies are being developed, to this date, they are not sufficient to handle this growing problem [liou2013update].\n\n\nTo mitigate debris growth, studies recommend a removal rate of five heavy debris per year [flury2001updated]. Many approaches have been proposed to remove or “deorbit” these debris. A promising method is Active Debris Removal (ADR). ADR missions are performed by an Orbital Transfer Vehicle (OTV), which can visit and de-orbit multiple debris during a single mission.\nDue to high costs, ADR missions should be able to maximise debris removal per mission at minimal cost. However, finding the optimal planning for de-orbiting several debris is non-trivial and requires adapted tools to find the most adequate plans. In addition, these missions require a high level of autonomous planning capabilities for the robotic spacecraft to be able to adapt to changing orbital conditions and mission requirements rapidly and effectively.\n\n\nThe ADR mission planning problem can be formulated as a Cost-Constrained Traveling Salesman Problem (CCTSP) [sokkappa1991cost], a variant of the Traveling Salesman Problem (TSP) [gavish1978travelling]. Key constraints are the mission duration and the propellant available to the OTV. As the OTV transfers from one debris to the next, it consumes both time and propellant. Each debris is given a value, allowing the mission designer to prioritise for a certain goal, such as debris size [yang2019rl_for_adr] or collision risk. The objective is, therefore, to optimise the debris sequence for maximum mission value under these constraints.\n\n\nTraditional optimisation models of ADR missions focus on minimising the mission cost using static methods. However, recent AI advancements, particularly in reinforcement learning (RL), allow the consideration of a dynamic approach. RL allows sequential decision-making and adaptability to new information [ai2022deep]. Applying RL to ADR mission planning is relevant since OTVs receive ongoing monitoring data and may need to update plans accordingly, ensuring their capacity to operate autonomously.\n\n\nResearch in ADR mission planning varies mainly in transfer strategy and optimisation approach. Ion thrusters for Low-Thrust transfers and chemical propulsion for High-Thrust transfers have been studied using various static optimisation methods [zuiani2012preliminary][medioni2023trajectory]. RL frameworks, such as Deep Q-Network (DQN) [mnih2013playing], have shown promise in optimising debris selection dynamically, but their adaptive capabilities need further exploration [yang2019rl_for_adr][yang2020ucbts].\n\n\nThis paper aims to explore the adaptive capabilities of an RL-controlled ADR mission. The initial objective is to create an RL environment for High-Thrust ADR missions. Subsequently, the study shows that an agent can be trained to autonomously respond according to new information obtained during the mission.\n\n'
    )
