import datetime
from unittest.mock import MagicMock, patch

from research_town.utils.paper_collector import (
    get_daily_papers,
    get_paper_content_from_html,
    get_paper_introduction,
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


def test_get_paper_content_from_html() -> None:
    sections = get_paper_content_from_html('https://arxiv.org/html/2403.05534v1')
    assert sections is not None
    assert '1 Introduction' in sections
    assert len(sections['1 Introduction']) > 0


def test_get_paper_introduction() -> None:
    test_url1 = 'https://arxiv.org/pdf/2409.16928'
    test_url2 = 'https://openreview.net/pdf?id=NnMEadcdyD'
    test_url3 = 'https://arxiv.org/abs/2409.17012'
    intro1 = get_paper_introduction(test_url1)
    intro2 = get_paper_introduction(test_url2)
    intro3 = get_paper_introduction(test_url3)
    assert (
        intro1
        == 'Introduction\nIn natural language processing, the two main challenges in developing new models are the difficulty in\nacquiring high-quality data and the extensive training times required to make models more expressive[ 1].\nThis work focuses on the latter issue. We experiment with unconventional computing architectures,\nthe goal being to assess if and how they can help accelerate training time to obtain more expressive\nmodels. To this purpose, our choice is architectures that develop Adiabatic Quantum Computing (AQC),\nwhere the technology proposed by D-Wave is considered a standard. The reason is twofold. On one\nside AQC by its very nature solves minimization problems in the QUBO form (Quadratic Unconstrained\nBinary Optimization). On the other, the core of many AI problems is minimizing some functions by\nlooking for the values of specific parameters.\nWe choose SVM[ 2] over more standard Transformers models because preliminary investigations on\nSVMs that leverage AQC already exist[ 3] and SVM share some similarities with the attention mechanism\nof Transformers[4].\nPrecalling that, among classification tasks in natural language processing, the binary version of\nSentiment Analysis (BSA) aims to separate sentences that convey “positive” emotions from those that\nconvey “negative” emotions. We reduced the BSA to QUBO and evaluated the following: 1) performance\nduring classification; 2) the time required to train the model; 3) the time required to classify new examples,\ncompared to more standard techniques implemented with heuristics and classical architectures. To\novercome the limited use of the quantum process unit (QPU) by the D-Wave hybrid solver, we also\nstarted to investigate algebraic-based alternatives to the proprietary mechanisms that split QUBO\nproblems between QPU and CPU.\n2. Quantum Support Vector Machine for Sentiment Analysis\nWe choose TweetEval[ 5] to verify the effectiveness of SVM for BSA. TweetEval is considered a standard\nfor comparing different models and contains a sufficiently large and representative number of examples,\ni.e. Tweets extracted from https://x.com/ and labelled automatically. The “sentiment” split of TweetEval\nBigHPC2024: Special Track on Big Data and High-Performance Computing, co-located with the 3rdItalian Conference on Big Data\nand Data Science, ITADATA2024, September 17 – 19, 2024, Pisa, Italy.\n/envel⌢pe-⌢penmario.bifulco@edu.unito.it (M. Bifulco); luca.roversi@unito.it (L. Roversi)\n/gl⌢behttps://github.com/TheFlonet/qsvm4sentanalysis (M. Bifulco); https://www.di.unito.it/~rover/ (L. Roversi)\n/orcid0000-0002-1871-6109 (L. Roversi)\n©2024 Copyright for this paper by its authors. Use permitted under Creative Commons License Attribution 4.0 International (CC BY 4.0).arXiv:2409.16928v1  [cs.AI]  25 Sep 2024includes three classes: positive, negative and neutral. We choose to discard all “neutral” samples to avoid\nintroducing errors during learning due to examples belonging to non-expressive classes. Additionally,\nwe normalize the quantity of elements in the positive and negative classes to ensure a balanced dataset.\nSince SVMs do not natively support text processing, it is necessary to compute embeddings. Among\nthe various possibilities, SentenceBert[ 6] allows for capturing the contextual information of the entire\nsentence by producing a single embedding.\nFor comparison with the classical counterpart, we choose: 1) the CPLEX[ 7] solver, a widely used\noptimizer for solving both linear and non-linear programming problems; 2) RoBERTa[ 8], a deep-learning\nmodel based on BERT[ 9] and the attention mechanism[ 10]. RoBERTa allows a fair comparison as the\nmodel we use[11] is fine-tuned on TweetEval.\nBelow are the'
    )
    assert (
        intro2
        == 'Introduction\nDiffusion-based generative models, or diffusion models in short, were ﬁrst introduced by Sohl-\nDickstein et al. [2015]. After years of relative obscurity, this class of models suddenly rose to\nprominence with the work of Song and Ermon [2019] and Ho et al. [2020] who demonstrated that,\nwith further reﬁnements in model architectures and objective functions, diffusion models can perform\nstate-of-the-art image generation.\n37th Conference on Neural Information Processing Systems (NeurIPS 2023).\n(a) 512\x02512\n (b) 256\x02256\n (c) 128\x02128\nFigure 1: Samples generated from our VDM++ diffusion models trained on the ImageNet dataset;\nsee Section 5 for details and'
    )
    assert (
        intro3
        == 'Introduction\nIn recent years, Low Earth Orbit (LEO) has become\nincreasingly crowded with debris originating from\nspacecraft fragmentation at the end of their opera-\ntional life cycle. Collisions of such debris with space\nassets can often lead to catastrophic failure. One ex-\nample is the Cosmos 2251-Iridium 33, which led to\nthe destruction of the Iridium 33 satellite and added\nmore than 2000 pieces of debris to LEO [1]. In ad-\ndition, collisions between objects generate new space\ndebris, increasing the likelihood of further collisions,\nin what is known as the Kessler e ffect [2]. Although\ninternational post-mission disposal policies are being\ndeveloped, to this date, they are not su fficient to han-\ndle this growing problem [3].\nTo mitigate debris growth, studies recommend a re-\nmoval rate of five heavy debris per year [4]. Many ap-\nproaches have been proposed to remove or “deorbit”\n∗Equal contributions.\n†Corresponding author. E-Mail: adam.abdin@centralesupelec.frthese debris. A promising method is Active Debris Re-\nmoval (ADR). ADR missions are performed by an Or-\nbital Transfer Vehicle (OTV), which can visit and de-\norbit multiple debris during a single mission. Due to\nhigh costs, ADR missions should be able to maximise\ndebris removal per mission at minimal cost. However,\nfinding the optimal planning for de-orbiting several\ndebris is non-trivial and requires adapted tools to find\nthe most adequate plans. In addition, these missions\nrequire a high level of autonomous planning capabil-\nities for the robotic spacecraft to be able to adapt to\nchanging orbital conditions and mission requirements\nrapidly and e ffectively.\nThe ADR mission planning problem can be formu-\nlated as a Cost-Constrained Traveling Salesman Prob-\nlem (CCTSP) [5], a variant of the Traveling Salesman\nProblem (TSP) [6]. Key constraints are the mission\nduration and the propellant available to the OTV. As\nthe OTV transfers from one debris to the next, it con-\nsumes both time and propellant. Each debris is given\na value, allowing the mission designer to prioritise for\na certain goal, such as debris size [7] or collision risk.\nThe objective is, therefore, to optimise the debris se-\nquence for maximum mission value under these con-\nstraints.\nTraditional optimisation models of ADR missions\nfocus on minimising the mission cost using static'
    )
