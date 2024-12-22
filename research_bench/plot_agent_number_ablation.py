import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Example data
researcher_numbers = [1, 2, 3, 4, 5]
openai_similarity_scores = [47.59, 51.54, 52.36, 52.59, 52.75]
voyageai_similarity_scores = [53.01, 55.05, 56.36, 56.77, 57.18]

# Set a seaborn style for consistency
sns.set_theme(style="whitegrid")

# Create the plot
fig, ax = plt.subplots(figsize=(6, 4))

# Line plot for OpenAI scores
sns.lineplot(
    x=researcher_numbers,
    y=openai_similarity_scores,
    marker='o',
    color=sns.color_palette("pastel")[1],
    ax=ax,
    label='text-embedding-large-3',
    linewidth=4,  # Make the line thicker
    markersize=10   # Make the dots larger
)

# Line plot for VoyageAI scores
sns.lineplot(
    x=researcher_numbers,
    y=voyageai_similarity_scores,
    marker='o',
    color=sns.color_palette("pastel")[0],
    ax=ax,
    label='voyage-3',
    linewidth=4,  # Make the line thicker
    markersize=10   # Make the dots larger
)

# Add titles and labels
ax.set_xlabel("Researcher Number for Paper Writing", fontsize=20)
ax.set_ylabel("Similarity Score", fontsize=20)

# Add y-axis limits for consistency with the bar plot
ax.set_ylim(47, 59)
ax.set_xlim(0.5, 5.5)

# Tweak the x-axis to have integer ticks
ax.set_xticks(researcher_numbers)
ax.set_xticklabels(researcher_numbers, fontsize=15)

# Add a legend
ax.legend(fontsize=12)

# Add labels near each point for OpenAI scores
for x, y in zip(researcher_numbers, openai_similarity_scores):
    ax.annotate(f'{y:.1f}',
                xy=(x, y),
                xytext=(0, 5),
                textcoords="offset points",
                ha='center',
                fontsize=15)

# Add labels near each point for VoyageAI scores
for x, y in zip(researcher_numbers, voyageai_similarity_scores):
    ax.annotate(f'{y:.1f}',
                xy=(x, y),
                xytext=(0, 5),
                textcoords="offset points",
                ha='center',
                fontsize=15)

# Tweak y-axis ticks for a clean look
ax.set_yticks(np.arange(47, 59.1, 2))
ax.grid(False)

# Adjust layout and save the figure
plt.tight_layout()
plt.savefig("ablation_study_on_agent_number_with_seaborn_voyage.pdf")
plt.show()
