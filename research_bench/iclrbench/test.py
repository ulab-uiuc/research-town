import json
from voyageai.client import Client

# Define the text inputs
text_1 = """
Teach LLMs to Phish: Stealing Private
"""

text_2 = """
I am a researcher specializing in collaborative causal inference (CCI), where I focus on enhancing the estimation of causal effects by leveraging data from multiple self-interested parties. My work addresses the critical challenge of incentivizing these parties to share their valuable proprietary data, which is often costly to obtain. To tackle this, I have developed a reward scheme grounded in the unique statistical properties essential for causal inference.

My approach involves creating a data valuation function that assesses the contribution of each party based on how closely their data aligns with the treatment effect estimates derived from aggregated data. By employing a modified version of the Shapley value, I ensure that rewards are distributed fairly and reflect the true value of each party's contribution. This innovative framework not only guarantees fairness but also enhances the accuracy of treatment effect estimates through improved, stochastically perturbed outputs.

Through empirical validation using both simulated and real-world datasets, I have demonstrated the effectiveness of my reward scheme, paving the way for more collaborative and efficient causal inference practices. My research aims to bridge the gap between data privacy concerns and the need for robust causal analysis, ultimately fostering a more cooperative environment for data sharing in the pursuit of scientific knowledge.
"""

# Initialize the client
client = Client()

# Embed the two texts
embeddings = client.embed([text_1, text_2], input_type='document', model='voyage-3')
embedding_1, embedding_2 = embeddings.embeddings

# Define the cosine similarity function
def cosine_similarity(vec1, vec2):
    return sum(a * b for a, b in zip(vec1, vec2)) / (
        (sum(a * a for a in vec1) ** 0.5) * (sum(b * b for b in vec2) ** 0.5)
    )

# Compute the similarity
similarity = cosine_similarity(embedding_1, embedding_2)

# Output the similarity
print(f"Cosine similarity between the two texts: {similarity:.4f}")
