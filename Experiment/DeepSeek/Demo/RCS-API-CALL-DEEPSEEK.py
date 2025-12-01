import requests
import json
import pandas as pd
import time


# Global Constants

API_KEY = "DEEPSEEK_API_KEY_HERE"  # We must replace API here
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

# Considering 1000 responses per question
N_SAMPLES = 1000

# Delay between requests to avoid rate limits
REQUEST_DELAY = 0.25


# Base function: Single DeepSeek API call

def ask_deepseek(prompt, temperature=0.9):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature
    }

    response = requests.post(DEEPSEEK_URL, headers=headers, data=json.dumps(payload))
    response.raise_for_status()  # raises error if any API issue occurs

    return response.json()["choices"][0]["message"]["content"].strip()



# Sampling responses for free-text survey questions

def sample_responses(question_text, n=N_SAMPLES):
    prompt = (
        "Answer the following survey question as a human respondent.\n"
        "Respond *only* with the answer, with no explanation.\n\n"
        f"Question: {question_text}\n"
    )

    responses = []
    for i in range(n):
        answer = ask_deepseek(prompt, temperature=0.9)
        responses.append(answer)
        time.sleep(REQUEST_DELAY)

        if (i+1) % 100 == 0:
            print(f"  → {i+1}/{n} responses collected")

    return responses


# Likert-style responses

def force_numeric(question_text, scale_min=1, scale_max=10, n=N_SAMPLES):
    prompt = (
        f"You MUST answer with a single integer between {scale_min} and {scale_max}.\n"
        "Do NOT explain your choice.\n\n"
        f"Question: {question_text}\n"
        "Answer ONLY with a number."
    )

    responses = []
    for i in range(n):
        answer = ask_deepseek(prompt, temperature=1.0)
        responses.append(answer)
        time.sleep(REQUEST_DELAY)

        if (i+1) % 100 == 0:
            print(f"  → {i+1}/{n} numerical responses collected")

    return responses


# Batch-run the entire survey dataset


def run_survey(csv_path):
    df = pd.read_csv(csv_path)

    all_outputs = {}

    for idx, row in df.iterrows():
        qid = str(row["id"])
        text = row["question"]
        qtype = row["type"]

        print(f"\n============================================================")
        print(f"Processing {qid}: {text}")
        print(f"Question type: {qtype}")
        print("============================================================")

        # Route to correct function
        if qtype == "numeric":
            outputs = force_numeric(text, scale_min=1, scale_max=10)
        elif qtype == "free":
            outputs = sample_responses(text)
        else:
            raise ValueError(f"Unknown question type: {qtype}")

        # Save results for this item
        all_outputs[qid] = {
            "question": text,
            "type": qtype,
            "responses": outputs
        }

    return all_outputs


# Save results to JSON file


def save_results(results_dict, outfile="deepseek_wvs_results.json"):

    with open(outfile, "w") as f:
        json.dump(results_dict, f, indent=2)
    print(f"\n✔ Results saved to: {outfile}")


# MAIN EXECUTION


if __name__ == "__main__":

    print("\n==============================")
    print("  DeepSeek WVS Data Collector")
    print("==============================\n")

    # <<< WE MUST CHANGE IT TO OUR INPUT CSV >>>
    INPUT_CSV = "BFI2_questions.csv"

    results = run_survey(INPUT_CSV)
    save_results(results)

    print("\n🎉 Completed all items!")
