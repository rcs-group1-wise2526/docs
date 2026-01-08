import json
import pandas as pd
import time
import os
from mistralai import Mistral

API_KEY = "yxZ0v2Iuv1oRYHz9UeHpTSk9vI9Peoq3"
client = Mistral(api_key=API_KEY)
MODEL = "mistral-small-latest"

def create_bfi_prompt(item_text, language="en"):
    system_prompts = {
        "ch": """你正在完成人格问卷。

每个项目必须用1到5之间的单个数字回答，其中1表示强烈不同意，5表示强烈同意。

输出必须仅包含一个字符1、2、3、4或5。

不要写词语。

不要解释。

不要添加标点符号或空格。

如果你无法遵守，仍然输出1、2、3、4、5中的一个。""",
        "en": """You are completing a personality questionnaire.

You must answer every item with a single digit from 1 to 5, where 1 means strong disagreement and 5 means strong agreement.

Your output must contain ONLY one character 1, 2, 3, 4, or 5.

Do not write words.

Do not explain.

Do not add punctuation or spaces.

If you cannot comply, still output one of 1, 2, 3, 4, 5.""",
        "es": """Está completando un cuestionario de personalidad.

Debe responder cada elemento con un solo dígito del 1 al 5, donde 1 significa fuerte desacuerdo y 5 significa fuerte acuerdo.

Su respuesta debe contener SOLO un carácter 1, 2, 3, 4 o 5.

No escriba palabras.

No explique.

No agregue puntuación ni espacios.

Si no puede cumplir, aún así escriba uno de 1, 2, 3, 4, 5.""",
        "tr": """Bir kişilik anketi tamamlıyorsunuz.

Her öğeyi 1 ile 5 arasında tek bir rakamla yanıtlamalısınız; burada 1 güçlü anlaşmazlığı, 5 ise güçlü anlaşmayı ifade eder.

Çıktınız SADECE 1, 2, 3, 4 veya 5 karakterini içermelidir.

Kelime yazmayın.

Açıklama yapmayın.

Noktalama işareti veya boşluk eklemeyin.

Uyamıyorsanız, yine de 1, 2, 3, 4, 5'ten birini yazın."""
    }
    
    user_prompts = {
        "ch": f"按1到5的等级评分以下陈述：我是一个{item_text}的人。仅输出1、2、3、4或5中的一个字符。",
        "en": f"Rate the following statement on a scale from 1 to 5: I am someone who {item_text}. Output ONLY one character 1, 2, 3, 4, or 5.",
        "es": f"Califique la siguiente afirmación en una escala del 1 al 5: Soy alguien que {item_text}. Responda SOLO con uno de 1, 2, 3, 4 o 5.",
        "tr": f"Aşağıdaki ifadeyi 1'den 5'e puan verin: Ben {item_text} biri'yim. Sadece 1, 2, 3, 4 veya 5'ten birini yazın."
    }
    
    system_prompt = system_prompts.get(language, system_prompts["en"])
    user_prompt = user_prompts.get(language, user_prompts["en"])
    
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

def send_mistral_request(messages, temperature=0.0):
    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = client.chat.complete(
                model=MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=8
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[WARN] API error (attempt {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                wait_time = (2 ** attempt) * 2
                print(f"  Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
            else:
                return "ERROR"

def process_full_survey(items, language="en"):
    system_prompt_only = create_bfi_prompt("dummy", language=language)[0]["content"]
    conversation = [{"role": "system", "content": system_prompt_only}]
    answers = []
    
    for item_text in items:
        user_prompt_only = create_bfi_prompt(item_text, language=language)[1]["content"]
        conversation.append({"role": "user", "content": user_prompt_only})
        answer = send_mistral_request(conversation)
        conversation.append({"role": "assistant", "content": answer})
        answers.append(answer)
        time.sleep(1.5)
    
    return answers

def generate_multiple_surveys(csv_path, num_surveys=20, language="en"):
    df = pd.read_csv(csv_path)
    items = df['question'].tolist()
    all_results = []
    
    for survey_num in range(num_surveys):
        print(f"Generating Survey {survey_num+1}/{num_surveys} [{language.upper()}]")
        survey_answers = process_full_survey(items, language=language)
        all_results.append(survey_answers)
    
    return all_results

def store_survey_data(results, output_file):
    try:
        output_dir = os.path.dirname(output_file)
        print(f"  Output directory: {output_dir}")
        print(f"  Full output path: {output_file}")
        
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Results saved to {output_file}")
        print(f"  File size: {os.path.getsize(output_file)} bytes")
        
    except Exception as e:
        print(f"✗ Error saving to {output_file}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Mistral Sequential-Memory BFI-2 Generator (4 Languages)")
    
    INPUT_CSV = "BFI2_Questionnaire.csv"
    OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
    
    print(f"Working directory: {OUTPUT_DIR}")
    print(f"Looking for: {INPUT_CSV}")
    
    languages = {
        "ch": os.path.join(OUTPUT_DIR, "mistral_bfi2_results_ch.json"),
        "en": os.path.join(OUTPUT_DIR, "mistral_bfi2_results_en.json"),
        "es": os.path.join(OUTPUT_DIR, "mistral_bfi2_results_es.json"),
        "tr": os.path.join(OUTPUT_DIR, "mistral_bfi2_results_tr.json")
    }
    
    for lang, output_file in languages.items():
        print(f"\n--- {lang.upper()} ---")
        survey_results = generate_multiple_surveys(INPUT_CSV, num_surveys=20, language=lang)
        store_survey_data(survey_results, output_file)
    
    print("\nAll languages completed!")
