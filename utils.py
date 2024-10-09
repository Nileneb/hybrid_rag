import pandas as pd
from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch
import re

# Funktion zur Extraktion von Entitäten mit BioBERT
def extract_entities_with_biobert(text: str):
    """Extrahiert die Entitäten aus dem Text mit BioBERT."""
    tokenizer = AutoTokenizer.from_pretrained("dmis-lab/biobert-base-cased-v1.1")
    model = AutoModelForTokenClassification.from_pretrained("dmis-lab/biobert-base-cased-v1.1")

    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    outputs = model(**inputs)

    predictions = torch.argmax(outputs.logits, dim=2)
    tokens = tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])

    recognized_entities = []
    for token, prediction in zip(tokens, predictions[0]):
        if prediction.item() != 0:  # Nur wenn die Entität nicht 'O' (Other) ist
            recognized_entities.append(token)

    return recognized_entities

# Funktion zur Reinigung der extrahierten Entitäten
def clean_recognized_entities(entities):
    """Säubere die erkannte Entität und entferne unnötige Sonderzeichen oder Subtokens."""
    cleaned_entities = []
    for entity in entities:
        entity = re.sub(r"##", "", entity)  # Entferne Subtoken-Markierungen
        if entity.isalpha():  # Füge nur alphabetische Tokens hinzu
            cleaned_entities.append(entity)
    return cleaned_entities

# Dynamische Funktion zur Kategorisierung der Entitäten in PICO
def classify_pico_dynamic(entities, context: str):
    """Kategorisiert die Entitäten dynamisch in PICO basierend auf ihrem Kontext im Text."""
    
    pico = {
        'Population': [],
        'Intervention': [],
        'Comparison': [],
        'Outcome': []
    }

    for entity in entities:
        # Kontext-basierte dynamische Kategorisierung
        if context_contains_category(entity, 'Population', context):
            pico['Population'].append(entity)
        elif context_contains_category(entity, 'Intervention', context):
            pico['Intervention'].append(entity)
        elif context_contains_category(entity, 'Comparison', context):
            pico['Comparison'].append(entity)
        elif context_contains_category(entity, 'Outcome', context):
            pico['Outcome'].append(entity)

    return pico

# Hilfsfunktion zur dynamischen Kategoriebestimmung
def context_contains_category(entity: str, category: str, context: str) -> bool:
    """Verwendet den Textkontext, um zu bestimmen, ob eine Entität in eine PICO-Kategorie gehört."""
    # Hier wird in Zukunft eine Machine Learning Logik implementiert
    return True  # Platzhalter: Der Algorithmus zur dynamischen Kategoriebestimmung kommt hier rein

# Funktion zur Erstellung der x/y-Tabelle mit dynamischen Kategorien und Mesh-Terms
def generate_pico_mesh_table(pico_structure):
    """Erstellt eine x/y-Tabelle zur Darstellung der PICO-Kategorien und deren dynamischer Synonyme/Mesh-Terms."""
    
    table_data = {
        'PICO': ['Population', 'Intervention', 'Comparison', 'Outcome'],
        'Synonyms/Mesh-Terms': [
            pico_structure['Population'],
            pico_structure['Intervention'],
            pico_structure['Comparison'],
            pico_structure['Outcome']
        ]
    }

    # Erstellen eines DataFrame zur Visualisierung
    df = pd.DataFrame(table_data)
    return df

# Hauptfunktion zur Verarbeitung des Textes
def process_text_with_biobert_and_pico(text: str):
    """Hauptfunktion zur Verarbeitung des Textes und dynamischen Klassifizierung der Entitäten in PICO-Kategorien."""
    
    # Entitäten mit BioBERT extrahieren
    recognized_entities = extract_entities_with_biobert(text)

    # Entitäten bereinigen
    cleaned_entities = clean_recognized_entities(recognized_entities)

    # Bereinigte Entitäten in PICO-Kategorien einordnen
    pico_structure = classify_pico_dynamic(cleaned_entities, text)

    # PICO-Kategorien in eine x/y-Tabelle einfügen
    pico_mesh_table = generate_pico_mesh_table(pico_structure)

    # Tabelle zurückgeben
    return pico_mesh_table
