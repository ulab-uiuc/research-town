import json
import numpy as np
import matplotlib.pyplot as plt

num = 3

# Load and process without_bio data
with open(f'./results/agent_number_ablation_record_each_agent_output_paper_bench_with_bio_sample_5_result_4o_mini_fake_research_town.jsonl', 'r') as f:
    without_bio_results = [json.loads(line) for line in f]
    for res in without_bio_results:
        q1_agents = res['openai_sim_q1_per_agent']
        q2_agents = res['openai_sim_q2_per_agent']
        q3_agents = res['openai_sim_q3_per_agent']
        q4_agents = res['openai_sim_q4_per_agent']
        q5_agents = res['openai_sim_q5_per_agent']

        agents_scores = zip(q1_agents, q2_agents, q3_agents, q4_agents, q5_agents)

        avg_openai_sim = []
        for agent_scores in agents_scores:
            if 0 in agent_scores:
                continue
            avg_openai_sim.append(sum(agent_scores) / 5.0)

        res['avg_openai_sim'] = avg_openai_sim

all_averages_without_bio = [val for res in without_bio_results for val in res['avg_openai_sim']]

# Load and process with_bio data
with open(f'./results/agent_number_ablation_record_each_agent_output_paper_bench_with_bio_sample_1_result_4o_mini_fake_research_town.jsonl', 'r') as f:
    with_bio_results = [json.loads(line) for line in f]
    for res in with_bio_results:
        q1_agents = res['openai_sim_q1_per_agent']
        q2_agents = res['openai_sim_q2_per_agent']
        q3_agents = res['openai_sim_q3_per_agent']
        q4_agents = res['openai_sim_q4_per_agent']
        q5_agents = res['openai_sim_q5_per_agent']

        agents_scores = zip(q1_agents, q2_agents, q3_agents, q4_agents, q5_agents)

        avg_openai_sim = []
        for agent_scores in agents_scores:
            if 0 in agent_scores:
                continue
            avg_openai_sim.append(sum(agent_scores) / 5.0)

        res['avg_openai_sim'] = avg_openai_sim

all_averages_with_bio = [val for res in with_bio_results for val in res['avg_openai_sim']]

print('with bio')
print(len(all_averages_with_bio))
print('without bio')
print(len(all_averages_without_bio))

# Compute statistics
mean_without_bio = np.mean(all_averages_without_bio) if all_averages_without_bio else 0
std_without_bio = np.std(all_averages_without_bio) if all_averages_without_bio else 0

mean_with_bio = np.mean(all_averages_with_bio) if all_averages_with_bio else 0
std_with_bio = np.std(all_averages_with_bio) if all_averages_with_bio else 0

print("Overall statistics (without_bio):")
print("  Mean:", mean_without_bio)
print("  Std:", std_without_bio)

print("Overall statistics (with_bio):")
print("  Mean:", mean_with_bio)
print("  Std:", std_with_bio)

# Create violin plot
data = [all_averages_without_bio, all_averages_with_bio]
plt.violinplot(data, showmeans=True, showextrema=True, showmedians=False)

plt.xticks([1, 2], ['Without Bio', 'With Bio'])
plt.title('Distribution of Per-Agent Average Similarities')
plt.xlabel('Condition')
plt.ylabel('Average OpenAI Similarity')

plt.show()
