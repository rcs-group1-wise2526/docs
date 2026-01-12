import json
import pandas as pd
import time
import os
from mistralai import Mistral

API_KEY = "YOUR API KEY"
client = Mistral(api_key=API_KEY)
MODEL = "mistral-small-latest"

prompts = {
    "ch": {
        "systemprompt": "py systemprompt 这是一个人格问卷。你需要对每个陈述用1到5中的一个数字进行回答，其中1表示非常不同意，5表示非常同意。只需回复一个数字，不要解释或添加其他内容。 userprompt f{itemtext}",
        "userprompt": "f{itemtext}"
    }
}

def create_bfi_prompt(item_text, language="ch"):
    system_prompt = prompts[language]["systemprompt"]
    user_prompt = prompts[language]["userprompt"].format(itemtext=item_text)
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

def send_mistral_request(messages, temperature=1, max_retries=5):
    for attempt in range(max_retries):
        try:
            response = client.chat.complete(
                model=MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=8,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"WARN: API error, attempt {attempt + 1}/{max_retries}: {e}")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
            else:
                return "ERROR"

def process_full_survey(items, language="ch"):
    system_prompt_only = create_bfi_prompt("dummy", language)[0]["content"]
    conversation = [{"role": "system", "content": system_prompt_only}]
    answers = []

    for item_text in items:
        user_prompt_only = create_bfi_prompt(item_text, language)[1]["content"]
        conversation.append({"role": "user", "content": user_prompt_only})
        answer = send_mistral_request(conversation)
        conversation.append({"role": "assistant", "content": answer})
        answers.append(answer)
        time.sleep(0.75)

    return answers

def generate_multiple_surveys(csv_path, num_surveys=100, language="ch"):
    df = pd.read_csv(csv_path)
    items = df["question"].tolist()
    all_results = []

    for survey_num in range(num_surveys):
        print(f"Generating Survey {survey_num + 1}/{num_surveys} ({language.upper()})")
        survey_answers = process_full_survey(items, language=language)
        all_results.append(survey_answers)

    return all_results

def store_survey_data(results, output_file):
    try:
        output_dir = os.path.dirname(output_file)
        print(f"Output directory: {output_dir}")
        print(f"Full output path: {output_file}")
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"Results saved to {output_file}")
        print(f"File size: {os.path.getsize(output_file)} bytes")
    except Exception as e:
        print(f"Error saving to {output_file}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Mistral BFI-2 Generator (CHINESE)")
    INPUT_CSV = "BFI2Questionnaire.csv"
    OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
    print(f"Working directory: {OUTPUT_DIR}")
    output_file = os.path.join(OUTPUT_DIR, "mistral_bfi2_results_ch.json")
    print(f"--- CH ---")
    survey_results = generate_multiple_surveys(INPUT_CSV, num_surveys=100, language="ch")
    store_survey_data(survey_results, output_file)
    print("CH completed!")
