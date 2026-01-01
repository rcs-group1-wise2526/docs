import requests
import json
from openai import OpenAI
import pandas as pd
import time


# Configuration
client = OpenAI(api_key="API KEY")
model = 'gpt-5.1' 
temperature = 1 


def prompt(item_text):

    system_prompt = (
        "Bu bir kişilik anketidir. \n"
        "Her ifade için 1-5 arası tek bir rakam yazın:\n1 = Kesinlikle katılmıyorum\n2 = Katılmıyorum\n3 = Kararsızım\n4 = Katılıyorum\n5 = Kesinlikle katılıyorum \n"
        "SADECE tek bir rakam yazın (1, 2, 3, 4 veya 5). \n" 
        "Açıklama yapmayın."
    )

    user_prompt = (
        f"Ben ... biriyim: {item_text}."
    )

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]



# GPT API Call

def call_model(model_input):
    try:
            response = client.chat.completions.create(
                model=model,
                messages=model_input,
                temperature=temperature,
            )
            return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error for prompt '{prompt}': {e}")
        return "ERROR"



# RUN ONE FULL SURVEY (60 ITEMS, SEQUENTIAL MEMORY)

def run_single_survey(items):
    # Extract system prompt once
    system_prompt_only = prompt("")[0]["content"]

    # Start fresh memory for this run
    conversation = [
        {"role": "system", "content": system_prompt_only}
    ]

    answers = []

    for item_text in items:
        # Build only the user prompt
        user_prompt_only = prompt(item_text)[1]["content"]

        # Add item
        conversation.append(
            {"role": "user", "content": user_prompt_only}
        )

        # Ask model
        answer = call_model(conversation)

        # Store answer in memory
        conversation.append(
            {"role": "assistant", "content": answer}
        )

        answers.append(answer)

        # Rate-limit safety
        time.sleep(0.25)

    return answers



# RUN MULTIPLE SURVEYS (RESET MEMORY EACH RUN)

def run_many_surveys(csv_path, n_runs=100):
    df = pd.read_csv(csv_path)
    items = df["question"].tolist()

    all_runs = []

    for run in range(n_runs):
        print(f"Running survey {run + 1}/{n_runs}")
        answers = run_single_survey(items)
        all_runs.append(answers)

    return all_runs



# SAVE RESULTS

def save_results(results, outfile="GPT_bfi2_results_tr.json"):
    with open(outfile, "w") as f:
        json.dump(results, f, indent=2)
    print("Results saved to:", outfile)


if __name__ == "__main__":
    results = run_many_surveys("BFI2_questions_GPT_tr.csv", n_runs=100)
    save_results(results)
    print("All runs completed successfully.")