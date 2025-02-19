import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Example data
agent_numbers = [1, 3, 5]
voyage_strength = [65.14, 65.83, 66.01]
voyage_weakness = [60.95, 61.29, 61.39]

# Set a seaborn style for consistency
sns.set_theme(style="whitegrid")

# Create the plot
fig, ax1 = plt.subplots(figsize=(6, 4))

# Plot strengths
sns.lineplot(
    x=agent_numbers,
    y=voyage_strength,
    marker='o',
    color=sns.color_palette("pastel")[2],
    ax=ax1,
    legend=False,  # Suppress automatic legend
    linewidth=4,  # Make the line thicker
    markersize=10   # Make the dots larger
)

# Add y-axis on the right
ax2 = ax1.twinx()

# Plot weaknesses
sns.lineplot(
    x=agent_numbers,
    y=voyage_weakness,
    marker='o',
    color=sns.color_palette("pastel")[3],
    ax=ax2,
    legend=False,  # Suppress automatic legend
    linewidth=4,  # Make the line thicker
    markersize=10   # Make the dots larger
)

# Add titles and labels
ax1.set_xlabel("Researcher Number for Review Writing", fontsize=20)
ax1.set_ylabel("Strength Scores", fontsize=20, color="black")
ax2.set_ylabel("Weakness Scores", fontsize=20, color="black")

# Add y-axis limits
ax1.set_ylim(65, 66.5)
ax2.set_ylim(60, 61.5)
ax1.set_xlim(0.5, 5.5)
ax2.set_xlim(0.5, 5.5)
ax1.set_yticks(np.arange(65, 66.6, 0.5))
ax2.set_yticks(np.arange(60, 61.6, 0.5))
ax1.tick_params(axis='both', which='major', labelsize=15)
ax2.tick_params(axis='y', labelsize=15)

# Add a single legend manually
custom_lines = [
    plt.Line2D([0], [0], color=sns.color_palette("pastel")[2], marker='o', label='voyage-3 (strength)'),
    plt.Line2D([0], [0], color=sns.color_palette("pastel")[3], marker='o', label='voyage-3 (weakness)')
]
ax1.legend(handles=custom_lines, fontsize=12, loc='lower right')

# Annotate scores

for x, y in zip(agent_numbers, voyage_strength):
    ax1.annotate(f'{y:.1f}',
                 xy=(x, y),
                 xytext=(0, -15),
                 textcoords="offset points",
                 ha='center',
                 fontsize=15)
    
for x, y in zip(agent_numbers, voyage_weakness):
    ax2.annotate(f'{y:.1f}',
                 xy=(x, y),
                 xytext=(0, -15),
                 textcoords="offset points",
                 ha='center',
                 fontsize=15)
ax1.grid(False)
ax2.grid(False)

# Adjust layout and save the figure
plt.tight_layout()
plt.savefig("number_ablation_study_voyage_only.pdf")
plt.show()
