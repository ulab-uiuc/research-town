import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Path to your JSON lines file
# jsonl_file = "./results/crossbench_1205_filtered_result_4o_mini_fake_research_town.jsonl"
jsonl_file = "./results/oodbench_1203_filtered_result_4o_mini_fake_research_town.jsonl"

# Use seaborn's default style
sns.set_style("whitegrid")

averages = []

# Read the JSON lines file
with open(jsonl_file, "r") as f:
    for line in f:
        data = json.loads(line)
        
        # Extract the openai_sim values for q1 to q5
        q1 = data.get("openai_sim_q1")
        q2 = data.get("openai_sim_q2")
        q3 = data.get("openai_sim_q3")
        q4 = data.get("openai_sim_q4")
        q5 = data.get("openai_sim_q5")
        
        # If all values are present, compute the average
        if None not in [q1, q2, q3, q4, q5]:
            avg_score = (q1 + q2 + q3 + q4 + q5) / 5.0
            averages.append(avg_score)

plt.figure(figsize=(6, 4))

# Define custom bin edges
bin_edges = [0.35, 0.45, 0.55, 0.65, 0.75, 0.85]

# Plot a histogram of the averages with custom bins
ax = sns.histplot(averages, bins=bin_edges, kde=True, color="#2ca02c", edgecolor='white')

# Add labels and title
plt.xlabel("Similarity score", fontsize=20)
plt.ylabel("Frequency", fontsize=20)

# Adjust the size of tick labels
plt.tick_params(axis='both', which='major', labelsize=15)

# Add frequencies above each bar
for patch in ax.patches:
    height = patch.get_height()
    if height > 0:  # Only annotate non-empty bins
        ax.annotate(f'{int(height)}', 
                    (patch.get_x() + patch.get_width() / 2, height + 1), 
                    ha='center', va='bottom', fontsize=14, color='black')

# Make spines visible to create a box
for spine in ax.spines.values():
    spine.set_visible(True)  # Ensure all spines are visible
    spine.set_linewidth(1.5)  # Set line width for the box

# Disable grid for this plot
ax.grid(False)
ax.set_yticks(np.arange(0, 80, 20))
ax.set_ylim(0, 62)

plt.tight_layout()
plt.savefig("similarity_score_distribution_with_frequencies.pdf")
plt.show()
