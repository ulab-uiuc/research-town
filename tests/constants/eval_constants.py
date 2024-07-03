idea_constant_A = 'The idea behind Mamba is to improve upon existing foundation models in deep learning, which typically rely on the Transformer architecture and its attention mechanism. While subquadratic-time architectures like linear attention, gated convolution, recurrent models, and structured state space models (SSMs) have been developed to address the inefficiency of Transformers on long sequences, they have not matched the performance of attention-based models in key areas such as language processing. Mamba addresses the shortcomings of these models by enabling content-based reasoning and making several key improvements: Adaptive SSM Parameters: By allowing SSM parameters to be functions of the input, Mamba effectively handles discrete modalities. This enables the model to selectively propagate or forget information along the sequence based on the current token.Parallel Recurrent Algorithm: Despite the changes preventing the use of efficient convolutions, Mamba employs a hardware-aware parallel algorithm in recurrent mode to maintain efficiency.Simplified Architecture: Mamba integrates these selective SSMs into a streamlined neural network architecture that does not rely on attention or MLP blocks.'

trend_constant_A = 'The current research trend in foundation models (FMs) involves developing large models that are pretrained on extensive datasets and then adapted for various downstream tasks. These FMs are primarily based on sequence models, which process sequences of inputs across different domains such as language, images, speech, audio, time series, and genomics. The predominant architecture for these models is the Transformer, which utilizes self-attention mechanisms. The strength of self-attention lies in its ability to handle complex data by routing information densely within a context window. However, this comes with significant limitations: difficulty in modeling outside of a finite context window and quadratic scaling with respect to window length.\n Efforts to create more efficient variants of attention have been extensive but often compromise the effectiveness that self-attention provides. As a result, no alternative has yet matched the empirical success of Transformers across various domains.Recently, structured state space models (SSMs) have emerged as a promising alternative. These models combine elements of recurrent neural networks (RNNs) and convolutional neural networks (CNNs), drawing from classical state space models. SSMs can be computed efficiently, either as recurrences or convolutions, and they scale linearly or near-linearly with sequence length. They also have mechanisms for modeling long-range dependencies, particularly excelling in benchmarks like the Long Range Arena.\nDifferent variants of SSMs have been successful in continuous signal data domains such as audio and vision. However, they have not been as effective in handling discrete and information-dense data, such as text, highlighting an area for further research and development.'

paper_title_constant_A = (
    'Mamba: Linear-Time Sequence Modeling with Selective State Spaces'
)

paper_abstract_constant_A = "Foundation models, now powering most of the exciting applications in deep learning, are almost universally based on the Transformer architecture and its core attention module. Many subquadratic-time architectures such as linear attention, gated convolution and recurrent models, and structured state space models (SSMs) have been developed to address Transformers' computational inefficiency on long sequences, but they have not performed as well as attention on important modalities such as language. We identify that a key weakness of such models is their inability to perform content-based reasoning, and make several improvements. First, simply letting the SSM parameters be functions of the input addresses their weakness with discrete modalities, allowing the model to selectively propagate or forget information along the sequence length dimension depending on the current token. Second, even though this change prevents the use of efficient convolutions, we design a hardware-aware parallel algorithm in recurrent mode. We integrate these selective SSMs into a simplified end-to-end neural network architecture without attention or even MLP blocks (Mamba). Mamba enjoys fast inference (5X higher throughput than Transformers) and linear scaling in sequence length, and its performance improves on real data up to million-length sequences. As a general sequence model backbone, Mamba achieves state-of-the-art performance across several modalities such as language, audio, and genomics. On language modeling, our Mamba-3B model outperforms Transformers of the same size and matches Transformers twice its size, both in pretraining and downstream evaluation."

review_constant_A = """Summary:
This paper proposes Mamba, which is a linear-time sequence model with selective state spaces. The authors propose to modify conventional state space models (SSMs) such that the modified models are input-dependent. The authors further propose engineering techniques for performance optimization. Experiments are conducted to demonstrate the effectiveness of the proposed method. In particular, several flavors of pre-trained models are provided.

Soundness: 2 fair
Presentation: 3 good
Contribution: 2 fair
Strengths:
The proposed Mamba method includes a simple modification to the conventional SSM model: add additional models to make SSM models dependent on the inputs. SSMs are known for their computational difficulties, and the authors address this issue by several performance optimization techniques.

The authors pre-train several variants of Mamba, ranging from 130M parameters to 1.4B parameters. These pre-trained models show performance improvements compared with the baselines in the paper.

Weaknesses:
Concerns about model design:

The motivation of Mamba is to address the drawbacks of recurrent models while improving the efficiency of attention-based models. There are many works following the same direction: S4-diagonal [1], SGConv [2], MEGA [3], SPADE [4], and many efficient Transformer models (e.g., [5]). All of these models achieve near linear complexity, and the authors need to compare Mamba with these works in terms of both model performance and efficiency. For model performance, some simple experiments such as language modeling on Wikitext-103 should suffice.

Many attention-based Transformer models show length generalization ability, i.e., models can be trained on a shorter sequence length and tested on a longer sequence length. Some examples include relative positional encoding (T5) and Alibi [6]. Because SSMs are in general sequential, does Mamba have this length generalization ability?

Concerns about experiments:

The authors need to compare with stronger baselines. The authors acknowledge that H3 was used as a motivation for the model architecture. However, they did not compare with H3 in the experiments. From Table 4 in [7], ppl of H3 is 8.8 (125M), 7.1 (355M), and 6.0 (1.3B) on the Pile dataset, which are considerably better than Mamba. The authors need to show comparisons with H3.

For the pre-trained models, the authors only show results on zero-shot inference. This setting is quite limited and the results cannot support the effectiveness of Mamba well. I suggest the authors run more long-sequence experiments such as document summarization, where the input sequence is naturally long (e.g., the average sequence length of the arXiv dataset is greater than 8k).

One of the main contributions that the authors claim is long sequence modeling. The authors should compare with more baselines on LRA (Long Range Arena), which is essentially the standard benchmark for long sequence understanding.

Memory benchmarking is missing. Even though Section 4.5 is titled “speed and memory benchmark”, only speed comparisons are presented. Also, the authors should provide more detailed setups of Figure 8 left, e.g., model layers, model sizes, details of the convolution, etc. Could the authors provide some intuitions why FlashAttention is the slowest when the sequence length is very large (Figure 8 left)?

[1] https://arxiv.org/pdf/2203.14343.pdf
[2] https://arxiv.org/pdf/2210.09298.pdf
[3] https://arxiv.org/pdf/2209.10655.pdf
[4] https://arxiv.org/pdf/2212.08136.pdf
[5] https://arxiv.org/pdf/2202.10447.pdf
[6] https://arxiv.org/pdf/2108.12409.pdf
[7] https://arxiv.org/pdf/2212.14052.pdf

Questions:
See above

Flag For Ethics Review: No ethics review needed.
Rating: 3: reject, not good enough
Confidence: 5: You are absolutely certain about your assessment. You are very familiar with the related work and checked the math/other details carefully.
Code Of Conduct: Yes
"""

review_constant_B = """
Summary:
The paper proposes a new class of selective state space models (SSMs) for sequence modeling that achieves Transformer-quality performance while scaling linearly in sequence length. The paper addresses the key problem in SSMs for selecting data by selecting particular inputs. The paper presents a hardware-aware algorithm that computes the model recurrently with a scan instead of convolution, avoiding materializing the expanded state to reduce memory usage. This results in faster computation than previous methods.

The paper simplifies prior deep sequence model architectures into a homogeneous architecture which is called as Mamba, incorporating the selective SSMs. Mamba enjoys fast inference, linear scaling, and improved performance on long sequences.

In the results the authors show that Mamba achieves state of the art on synthetic tasks, audio/genomics modeling, and language modeling and outperforms Transformers of the same size on language modeling in both pretraining and downstream tasks.

The results suggest selective SSMs and the Mamba architecture could be a strong candidate for a general sequence model backbone for foundation models across modalities. The paper demonstrates the potential for linear-time models to match or exceed the performance of quadratic Transformers.

Soundness: 3 good
Presentation: 3 good
Contribution: 3 good
Strengths:
A key limitation of prior SSMs is the inability to efficiently select data in an input-dependent manner. The paper introduces a key mechanism by parameterizing the SSM parameters based on the input, allowing the model to filter out irrelevant information and remember relevant information indefinitely.
The results as compared to Pythia, and Transforms on many benchmarks are impressive.
Weaknesses:
The model still has a quadratic memory requirement during training like Transformers.
Questions:
Have you evaluated scaling behavior beyond 1.4B parameters? How does it compare to Transformers at 10B scales?

The input selection mechanism introduces additional hyper parameters. How sensitive are the results to hyperparameters like the projection rank?

Flag For Ethics Review: No ethics review needed.
Rating: 6: marginally above the acceptance threshold
Confidence: 2: You are willing to defend your assessment, but it is quite likely that you did not understand the central parts of the submission or that you are unfamiliar with some pieces of related work. Math/other details were not carefully checked.
Code Of Conduct: Yes
"""

review_constant_C = """
Summary:
This paper upgrades S4 by making the token mixing matrix data-dependent and introduces the Mamba structure. On the other hand, although the use of FFT is not possible, the authors provide a linear algorithm for computation, resulting in linear computational complexity. The effectiveness of the proposed method is validated on multiple datasets.

Soundness: 4 excellent
Presentation: 4 excellent
Contribution: 4 excellent
Strengths:
The paper is written in a clear and understandable manner, with a well-defined approach and simple yet effective improvement strategies.

Weaknesses:
The paper lacks references to some relevant works, such as [1], [2], [3], [4] which discusses some Linear Attention methods, and [5], which is also a LongConv method. However, these references are completely absent in the paper. I suggest that the authors consider adding these citations to provide a more comprehensive review of related work.

[1] Zhen Qin, Weixuan Sun, Hui Deng, Dongxu Li, Yunshen Wei, Baohong Lv, Junjie Yan, Lingpeng Kong, and Yiran Zhong. cosformer: Rethinking softmax in attention. In ICLR, 2022.

[2] Efficient Attention via Control Variates, Lin Zheng, Jianbo Yuan, Chong Wang, and Lingpeng Kong In International Conference on Learning Representations (ICLR), 2023

[3] Linear Complexity Randomized Self-attention Mechanism, Lin Zheng, Chong Wang, and Lingpeng Kong In International Conference on Machine Learning (ICML), 2022

[4] Zhen Qin, Xiaodong Han, Weixuan Sun, Dongxu Li, Lingpeng Kong, Nick Barnes, and Yiran Zhong. The devil in linear transformer. In Proceedings of the 2022 Conference on Empirical Methods in Natural Language Processing, pages 7025-7041, Abu Dhabi, United Arab Emirates, Dec. 2022. Association for Computational Linguistics.

[5] Zhen Qin, Xiaodong Han, Weixuan Sun, Bowen He, Dong Li, Dongxu Li, Yuchao Dai, Lingpeng Kong, and Yiran Zhong. Toeplitz neural network for sequence modeling. In The Eleventh International Conference on Learning Representations (ICLR), 2023.

Questions:
1. Adding extrapolation experiments to the language model would be interesting.
The ablation analysis in Table 6 should be more comprehensive, with a total of $2^3$ possible combinations. I suggest that the authors include the remaining two combinations.
2. What's your setting of Scaling Law? Why is your ratio of token number and model size is the same as Chicilla's paper? I suppose the FLOPs of Transformers and SSMs would differ. Suppose the FLOPs of Transformers and SSMs would differ given the same amounts of total parameters, is this important to the final performance(accuracy)?
3. How did you parameterize the first convolutional layer in the Mamba-Block.
Providing more detailed implementation, such as offering core code, is very helpful.

Flag For Ethics Review: No ethics review needed.

Rating: 8: accept, good paper

Confidence: 5: You are absolutely certain about your assessment. You are very familiar with the related work and checked the math/other details carefully.
Code Of Conduct: Yes

"""


review_constant_D = """
Summary:
The authors study the recent state-space models (SSM) family of efficient sequence architectures and address some of their challenges, related to the inability to perform content-based reasoning. The core contribution of the work is the addition of a selection method to the SSM architecture, which results in simple and scalable architecture, Mamba. Then they demonstrate the superiority of Mamba on standard language benchmarks, as well as DNA and audio modeling. The authors also contribute efficient implementation and benchmarking of Mamba on modern hardware.

Soundness: 4 excellent
Presentation: 4 excellent
Contribution: 3 good
Strengths:
S1: The paper addresses very efficiently and effectively pressing problems in sequential modeling.

S2: The authors have identified simple toy tasks, such as selective copying and associative recall, that enable them to make design choices which state-of-the-art impact on real-world data.

S3: The connection to the role of gating mechanisms in RNNs is well-appreciated.

S4: The empirical part of the paper is very thorough, and the results are strong.

Weaknesses:
I do not identify any major weaknesses of the paper.

Questions:
I am curious if we could build a better understanding of the selection mechanism that you propose. In Theorem 1 you link that mechanism to gating in RNNs as a special case. Is it possible to understand better the generalization through some discussion / qualitative examples?

Flag For Ethics Review: No ethics review needed.
Rating: 8: accept, good paper
Confidence: 4: You are confident in your assessment, but not absolutely certain. It is unlikely, but not impossible, that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work.
Code Of Conduct: Yes
"""
