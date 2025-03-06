import json
import spacy
from fuzzywuzzy import fuzz
import os

def load_spacy_model():
    try:
        nlp = spacy.load("pt_core_news_sm")
    except Exception as e:
        print(f"Erro ao carregar o modelo spaCy: {e}")
        print("Tentando baixar o modelo...")
        os.system("python -m spacy download pt_core_news_sm")
        nlp = spacy.load("pt_core_news_sm")
    return nlp
nlp = load_spacy_model()

def load_intents():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, '..', 'data',
                                 'intents.json')
        print(f"Tentando carregar o arquivo de intenções de: {os.path.abspath(file_path)}")

        with open(file_path, 'r', encoding='utf-8') as file:
            intents = json.load(file)
        return intents
    except FileNotFoundError:
        raise Exception("Arquivo 'intents.json' não encontrado!")
    except json.JSONDecodeError:
        raise Exception("Erro ao decodificar o arquivo 'intents.json'.")


def preprocess_text(text: str) -> str:
    doc = nlp(text.lower())
    return " ".join([token.lemma_ for token in doc if not token.is_stop])


def find_best_match(question: str, intents: dict) -> tuple:
    preprocessed_question = preprocess_text(question)
    best_score = 0
    best_intent = None

    for intent, data in intents.items():
        for pattern in data["patterns"]:
            preprocessed_pattern = preprocess_text(pattern)
            score = fuzz.ratio(preprocessed_question, preprocessed_pattern)
            if score > best_score and score > 50:
                best_score = score
                best_intent = intent

    return best_intent, best_score


