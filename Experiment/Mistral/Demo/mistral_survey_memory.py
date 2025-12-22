import os
import json
import time
from mistralai.models import SDKError
import pandas as pd
from mistralai import Mistral 


# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MODEL_NAME = "mistral-small-latest"

# Number of synthetic respondents per item (start small while testing)
N_RESPONDENTS = 3
PAUSE_BETWEEN_CALLS = 2.0  # seconds

client = Mistral(api_key=MISTRAL_API_KEY)


# -------------------------------------------------------------------
# Core Mistral call with conversational context
# -------------------------------------------------------------------


def call_mistral_chat(history, temperature=0.9, max_retries=5):
    """
    Robust chat call with retry on rate limits (429) and backend errors (503).
    """
    for attempt in range(max_retries):
        try:
            response = client.chat.complete(
                model=MODEL_NAME,
                messages=history,
                temperature=temperature,
                stream=False,
            )
            return response.choices[0].message.content.strip()

        except SDKError as e:
            msg = str(e).lower()
            # rate limit or backend issues
            if "429" in msg or "rate limit" in msg or "503" in msg or "unreachable_backend" in msg:
                wait = 5 * (attempt + 1)
                print(f"[WARN] API issue ({e}), sleeping {wait}s then retry "
                      f"({attempt+1}/{max_retries})")
                time.sleep(wait)
            else:
                # different kind of error: re-raise immediately
                raise

    raise RuntimeError("Giving up after repeated API errors")


# -------------------------------------------------------------------
# Survey run: one coherent “respondent” across all items
# -------------------------------------------------------------------

def simulate_one_respondent(df):
    """
    Given a questionnaire DataFrame (id, question, type),
    return a dict qid -> single answer, where answers for all items
    come from the same conversational history.
    """
    answers = {}
    n_items = len(df)

    # Initialize shared context: one person doing a full survey
    conversation = [
        {
            "role": "system",
            "content": (
                "You are a single human participant completing an entire personality "
                "questionnaire. Answer as the same person across all items. "
                "For each question, follow the requested response format and do not "
                "add explanations."
            ),
        }
    ]

    for idx, row in df.iterrows():
        qid = str(row["id"])
        text = row["question"]
        qtype = row["type"]

        # Progress + item text
        conversation.append({
            "role": "user",
            "content": f"You are now answering item {idx+1} of {n_items}."
        })
        conversation.append({
            "role": "user",
            "content": text,
        })

        if qtype == "numeric":
            # Likert-style numeric answer
            conversation.append({
                "role": "user",
                "content": (
                    "Respond ONLY with a single whole number between 1 and 10. "
                    "Do not include any words or punctuation."
                )
            })
            reply = call_mistral_chat(conversation, temperature=1.0)
        else:
            # Free-text answer
            conversation.append({
                "role": "user",
                "content": (
                    "Answer this as if you were a typical survey respondent. "
                    "Write only the answer, without any explanation or extra text."
                )
            })
            reply = call_mistral_chat(conversation, temperature=0.9)

        # Store and extend history
        answers[qid] = reply
        conversation.append({"role": "assistant", "content": reply})
        time.sleep(PAUSE_BETWEEN_CALLS)

    return answers


# -------------------------------------------------------------------
# Top-level routine: multiple synthetic respondents
# -------------------------------------------------------------------

def generate_survey_dataset(csv_path):
    """
    Load questionnaire, repeatedly simulate respondents, and
    return a nested dict:
        {qid: {"question": ..., "type": ..., "responses": [r1, r2, ...]}}
    """
    df = pd.read_csv(csv_path)

    # Initialize result structure
    results = {
        str(row["id"]): {
            "question": row["question"],
            "type": row["type"],
            "responses": []
        }
        for _, row in df.iterrows()
    }

    for r_idx in range(N_RESPONDENTS):
        print(f"\n>>> Generating respondent {r_idx+1}/{N_RESPONDENTS}")
        respondent_answers = simulate_one_respondent(df)

        for qid, answer in respondent_answers.items():
            results[qid]["responses"].append(answer)

        if (r_idx + 1) % 10 == 0:
            print(f"    ...completed {r_idx+1} respondents")

    return results


# -------------------------------------------------------------------
# Saving helper
# -------------------------------------------------------------------

def export_results(data, filename="mistral_survey_memory.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Saved survey data to '{filename}'")


# -------------------------------------------------------------------
# Script entry point
# -------------------------------------------------------------------

if __name__ == "__main__":
    print("\n==========================================")
    print("  Mistral Survey Generator (with memory)")
    print("==========================================\n")

    QUESTIONNAIRE_CSV = "BFI2_Questionnaire.csv"

    survey_data = generate_survey_dataset(QUESTIONNAIRE_CSV)
    export_results(survey_data, filename="mistral_wvs_results_with_memory.json")

    print("\n🎉 Finished generating all synthetic respondents.")
