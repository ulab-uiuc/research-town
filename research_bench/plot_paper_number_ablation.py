import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Use Seaborn's style
sns.set_style("whitegrid")

# Data
settings = ["all", "related work", "introduction", "other"]
openai_means = np.array([0.6732, 0.6749, 0.6591, 0.5889])
voyage_means = np.array([0.6995, 0.7012, 0.6875, 0.6276])

# Number of bars (categories)
x = np.arange(len(settings))  # the label locations

# Set width of each bar
width = 0.35

# Create the plot
fig, ax = plt.subplots(figsize=(6, 4))

# Add bars using Seaborn-like colors for consistency
rects1 = ax.bar(x - width/2, voyage_means * 100, width, label='voyage-3', color=sns.color_palette("pastel")[0])
rects2 = ax.bar(x + width/2, openai_means * 100, width, label='text-embedding-large-3', color=sns.color_palette("pastel")[1])

# Set y-axis limits
ax.set_ylim(58, 73)

# Add labels, title, and tick labels
ax.set_ylabel('Similarity score', fontsize=20)
ax.set_xticks(x)
ax.set_xticklabels(settings, fontsize=15)
ax.legend(fontsize=12)

# Add a grid with Seaborn style
ax.grid(False)

plt.tick_params(axis='both', which='major', labelsize=15)

plt.xlabel("Cited paper for aggregation", fontsize=20)

# Function to add labels above bars
def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        ax.annotate(f'{height:.1f}',
                    xy=(rect.get_x() + rect.get_width()/2, height),
                    xytext=(0, 3),  # Offset
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=15)

# Add bar labels
autolabel(rects1)
autolabel(rects2)

ax.set_yticks(np.arange(58, 73, 4))

# Tight layout and save the figure
plt.tight_layout()
plt.savefig("ablation_study_on_paper_number_with_seaborn.pdf")
plt.show()
