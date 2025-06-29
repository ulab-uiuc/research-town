import json

with open("iclrbench_reviewers_filtered_bullets.json", "r", encoding="utf-8") as f:
    reviewers = json.load(f)
    keys = list(reviewers.keys())
    keys_100 = keys[:100]  # Select the first 8 reviewers for the subset
    reviewers_100 = {key: reviewers[key] for key in keys_100}  # Create a new dictionary with the first 8 reviewers
    with open("iclrbench_reviewers_filtered_bullets_100.json", "w", encoding="utf-8") as f_out:
        json.dump(reviewers_100, f_out, ensure_ascii=False, indent=4)