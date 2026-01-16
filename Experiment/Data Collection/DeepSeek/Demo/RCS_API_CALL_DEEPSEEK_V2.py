import requests
import json
import pandas as pd
import time


# API CONFIGURATION

API_KEY = "DEEPSEEK_API_KEY_HERE"      # We must replace this with our real DeepSeek API key
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"  # Endpoint for sending chat-style prompts


# BFI-2 Prompt Generator (Your Exact Preferred Prompts)

def build_bfi2_prompt(item_text):

    system_prompt = (
        "You are completing a personality questionnaire.\n"
        "You must answer every item with a single digit from 1 to 5, "
        "where 1 means strong disagreement and 5 means strong agreement.\n"
        "Your output must contain ONLY one character: 1, 2, 3, 4, or 5.\n"
        "Do not write words. Do not explain. Do not add punctuation or spaces.\n"
        "If you cannot comply, still output one of: 1, 2, 3, 4, 5."
    )

    user_prompt = (
        "Rate the following statement on a scale from 1 to 5:\n\n"
        f"\"I am someone who {item_text}.\"\n\n"
        "Output ONLY one character: 1, 2, 3, 4, or 5."
    )

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]


# DeepSeek API CALLER
# This sends our messages to DeepSeek

def ask_deepseek(messages, temperature=0.0):

    # Header telling DeepSeek who you are
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    # The actual request body
    payload = {
        "model": "deepseek-chat",
        "messages": messages, # messages: a list of system + user + previous answers
        "temperature": temperature
    }

    response = requests.post(DEEPSEEK_URL, headers=headers, data=json.dumps(payload)) # Send the request
    response.raise_for_status() # If anything went wrong, raise an error

    return response.json()["choices"][0]["message"]["content"].strip() # Extract ONLY the model’s text output. This should be "1" through "5"


# RUN ONE COMPLETE SURVEY (60 ITEMS) WITH MEMORY

def run_single_survey(items):

    # Extract ONLY the system prompt from our generator
    system_prompt_only = build_bfi2_prompt("")[0]["content"]

    # Start fresh conversation for this run
    conversation = [
        {"role": "system", "content": system_prompt_only}
    ]

    answers = []

    # Sequential memory answering
    for item_text in items:
        # Build user prompt (only the user part)
        user_prompt_only = build_bfi2_prompt(item_text)[1]["content"]

        # Add question to conversation history
        conversation.append({"role": "user", "content": user_prompt_only})

        # Ask the model
        answer = ask_deepseek(conversation)

        # Add model answer to memory
        conversation.append({"role": "assistant", "content": answer})

        answers.append(answer)

        # Slow down to avoid API rate limits
        time.sleep(0.10)

    return answers



# RUN 1000 SURVEYS (RESET MEMORY EACH TIME)

def run_many_surveys(csv_path, n_runs=1000):

    # Load your CSV of BFI-2 questions
    df = pd.read_csv(csv_path)
    items = df["question"].tolist()

    # Prepare storage
    all_runs = []

    # Loop 1000 times
    for run in range(n_runs):
        print(f"\n===== Running Survey {run + 1}/{n_runs} =====")

        answers = run_single_survey(items)
        all_runs.append(answers)

    return all_runs


# SAVE RESULTS (Save to JSON)

def save_results(results, outfile="deepseek_bfi2_results.json"):

    with open(outfile, "w") as f:
        json.dump(results, f, indent=2)

    print("\n✔ Results saved to:", outfile)


# MAIN EXECUTION

if __name__ == "__main__":
    print("\n===========================================")
    print("   DeepSeek Sequential-Memory BFI-2 Runner ")
    print("===========================================\n")

    INPUT_CSV = "BFI2_questions.csv"  # Must contain column: question

    results = run_many_surveys(INPUT_CSV, n_runs=1000) # Run 1000 surveys
    save_results(results)

    print("\n🎉 Completed all DeepSeek BFI-2 Runs Successfully!")