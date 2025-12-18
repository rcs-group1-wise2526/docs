import requests
import json
import pandas as pd
import time


# API CONFIGURATION

API_KEY = "DEEPSEEK_API_KEY_HERE"
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"



# BFI-2 PROMPT GENERATOR (MINIMAL + RIGOROUS)

def build_bfi2_prompt(item_text):

    system_prompt = (
        "This is a personality questionnaire.\n"
        "For each statement, respond with a single digit from 1 to 5,\n"
        "where 1 means strong disagreement and 5 means strong agreement.\n"
        "Respond ONLY with a single digit. Do not explain."
    )

    user_prompt = (
        f"I am someone who {item_text}."
    )

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]



# DEEPSEEK API CALLER

def ask_deepseek(messages, temperature=0.0):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": temperature
    }

    response = requests.post(
        DEEPSEEK_URL,
        headers=headers,
        data=json.dumps(payload)
    )
    response.raise_for_status()

    return response.json()["choices"][0]["message"]["content"].strip()



# RUN ONE FULL SURVEY (60 ITEMS, SEQUENTIAL MEMORY)

def run_single_survey(items):
    # Extract system prompt once
    system_prompt_only = build_bfi2_prompt("")[0]["content"]

    # Start fresh memory for this run
    conversation = [
        {"role": "system", "content": system_prompt_only}
    ]

    answers = []

    for item_text in items:
        # Build only the user prompt
        user_prompt_only = build_bfi2_prompt(item_text)[1]["content"]

        # Add item
        conversation.append(
            {"role": "user", "content": user_prompt_only}
        )

        # Ask model
        answer = ask_deepseek(conversation)

        # Store answer in memory
        conversation.append(
            {"role": "assistant", "content": answer}
        )

        answers.append(answer)

        # Rate-limit safety
        time.sleep(0.1)

    return answers



# RUN MULTIPLE SURVEYS (RESET MEMORY EACH RUN)

def run_many_surveys(csv_path, n_runs=1000):
    df = pd.read_csv(csv_path)
    items = df["question"].tolist()

    all_runs = []

    for run in range(n_runs):
        print(f"Running survey {run + 1}/{n_runs}")
        answers = run_single_survey(items)
        all_runs.append(answers)

    return all_runs



# SAVE RESULTS

def save_results(results, outfile="deepseek_bfi2_results.json"):
    with open(outfile, "w") as f:
        json.dump(results, f, indent=2)
    print("Results saved to:", outfile)



# MAIN

if __name__ == "__main__":
    results = run_many_surveys("BFI2_questions.csv", n_runs=1000)
    save_results(results)
    print("All runs completed successfully.")
