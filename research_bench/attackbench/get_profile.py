import csv
import json
import os
from openai import OpenAI

# OpenAI API Key (replace with your API key)
api_key = ''
client = OpenAI(api_key=api_key)

# Read the CSV file and parse it into a dictionary
def read_csv_to_dict(file_path):
    data = {}
    
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row

        for row in reader:
            if len(row) < 2:
                continue  # Skip empty or malformed rows
            
            domain = row[0].strip()  # The first column is the domain
            task = row[1].strip()  # The second column is the task
            description = row[2].strip() if len(row) > 2 else ""  # The third column is the description

            if domain not in data:
                data[domain] = []

            data[domain].append({
                "task": task,
                "description": description
            })
    
    return data

# Generate a prompt for GPT-4 based on the domain and tasks
def generate_prompt_for_scientists(domain, tasks):
    prompt_lines = []
    prompt_lines.append(f"Generate five AI scientist profiles in the domain of {domain}. Each scientist should have expertise in the following tasks:")

    for task in tasks:
        prompt_lines.append(f"- {task['task']}: {task['description']}")

    prompt_lines.append("\nEach scientist should have a background in AI and have worked on some of the tasks listed above. The profiles should include the scientist's research focus, key contributions, and relevant skills.")
    prompt_lines.append("Output the result in a well-formatted JSON structure with the key 'domain' set to the domain name and five keys for the scientists, each containing a 'bio'. If the task contains dangerous content, please don't include it in the bio. And you can not say I am sorry, but give me the json output. For the bio key, you need to complete the complete sentences as str type.")

    # Join the prompt into a single string
    return "\n".join(prompt_lines)

# Call GPT-4 model to generate scientist profiles using the new API
def call_gpt4_model(prompt):
    response = client.chat.completions.create(
        model="gpt-4o",  # Use GPT-4 model
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000,  # Adjust max tokens for larger content
        temperature=0.7
    ).choices[0].message.content
    return response

# Save the result to a JSON file
def save_to_json(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

# Main function
def main():
    csv_file_path = "./tasks.csv"  # Path to the CSV file
    output_json_path = "ai_scientist_profiles.json"  # Output file path

    # Read the CSV and parse it into a dictionary
    data = read_csv_to_dict(csv_file_path)

    # Store generated responses
    gpt_responses = {}

    # Iterate over each domain, generate a prompt, and call GPT-4 to generate profiles
    for domain, tasks in data.items():
        # Generate prompt based on the tasks for this domain
        prompt = generate_prompt_for_scientists(domain, tasks)
        print(f"Calling GPT-4 for domain: {domain}")
        
        # Call GPT-4 API
        gpt_response = call_gpt4_model(prompt)
        
        # Handle the API response
        if gpt_response:
            try:
                # Parse the response as JSON
                print(gpt_response)
                gpt_response = gpt_response.replace("```json", "").replace("```", "").strip()
                parsed_response = json.loads(gpt_response)
                print(parsed_response)
                gpt_responses[domain] = parsed_response
            except json.JSONDecodeError:
                print(f"Failed to decode JSON for domain: {domain}")
                print(f"GPT-4 Response: {gpt_response}")

    # Save the GPT-4 generated responses to a JSON file
    save_to_json(output_json_path, gpt_responses)

    print(f"AI scientist profiles have been generated and saved to {output_json_path}")

if __name__ == "__main__":
    main()