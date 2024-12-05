from openai import OpenAI

client = OpenAI(
  base_url = "https://integrate.api.nvidia.com/v1",
  api_key = "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"
)

completion = client.chat.completions.create(
  model="nvidia/nv-embed-v1",
  messages=[{"role":"user","content":"Write a limerick about the wonders of GPU computing."}],
  temperature=0.2,
  top_p=0.7,
  max_tokens=1024,
  stream=True
)

for chunk in completion:
  if chunk.choices[0].delta.content is not None:
    print(chunk.choices[0].delta.content, end="")