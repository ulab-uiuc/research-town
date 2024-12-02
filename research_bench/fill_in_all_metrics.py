import jsonlines
from research_bench.eval import compute_bertscore_per_question
from tqdm import tqdm

file_path = './results/paper_bench_hard_500_result_4o_mini_fake_research_town.jsonl'

with jsonlines.open(file_path, 'r') as f:
    dataset = [line for line in f]

for data in tqdm(dataset):
    ref_proposal = data['ref_proposal']
    gen_proposal = data['gen_proposal']
    if 'bertscore_q1' not in data:
        bert_score_per_question = compute_bertscore_per_question(ref_proposal, gen_proposal)
        data['openai_sim_q1'] = bert_score_per_question[0]
        data['openai_sim_q2'] = bert_score_per_question[1]
        data['openai_sim_q3'] = bert_score_per_question[2]
        data['openai_sim_q4'] = bert_score_per_question[3]
        data['openai_sim_q5'] = bert_score_per_question[4]

with jsonlines.open(file_path, 'w') as f:
    for data in dataset:
        f.write(data)
