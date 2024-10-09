import requests
import os

# Funktion zum Senden von Suchanfragen an die PubMed API
def send_pubmed_search_query(query, retmax=2000):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        'db': 'pmc',
        'term': query,
        'retmode': 'json',
        'retmax': retmax
    }
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        result = response.json()['esearchresult']
        article_ids = result.get('idlist', [])
        total_results = int(result.get('count', 0))
        
        # Melde exakte Anzahl der Treffer zurück
        print(f"{total_results} Treffer für die Suchanfrage '{query}' gefunden.")
        
        # Steuerung der weiteren Verarbeitung basierend auf der Anzahl der Treffer
        if total_results < 20:
            print(f"Unter 20 Treffer gefunden ({total_results}), Studien werden heruntergeladen...")
            return article_ids, total_results
        else:
            print(f"{total_results} Treffer gefunden, lade nur die Titel und keine PDFs herunter.")
            return article_ids[:2000], total_results  # Gib maximal 2000 Artikel-IDs zurück zur Titelanzeige
    
    else:
        print(f"Fehler bei der Anfrage: {response.status_code}")
        return [], 0

# Funktion zum Empfangen der Studien-Titel von PubMed
def fetch_study_titles(article_ids):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    study_titles = []
    
    for article_id in article_ids:
        params = {
            'db': 'pmc',
            'id': article_id,
            'retmode': 'json'
        }
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            title = response.json()['result'][article_id].get('title', 'Kein Titel verfügbar')
            study_titles.append({'id': article_id, 'title': title})
        else:
            print(f"Fehler bei der Detailabfrage für {article_id}: {response.status_code}")
    
    return study_titles

# Funktion zum Herunterladen der PDF-Dateien von PubMed
def download_pdf(article_id, save_directory='./pdfs'):
    pdf_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{article_id}/pdf"
    response = requests.get(pdf_url)
    
    if response.status_code == 200:
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)
        
        pdf_path = os.path.join(save_directory, f"{article_id}.pdf")
        with open(pdf_path, 'wb') as f:
            f.write(response.content)
        print(f"PDF von Artikel {article_id} erfolgreich heruntergeladen: {pdf_path}")
    else:
        print(f"PDF für Artikel {article_id} nicht gefunden oder Fehler: {response.status_code}")

# Hauptfunktion, die die Suchanfrage an PubMed sendet, Ergebnisse analysiert und bei <20 Treffern die Studien herunterlädt
def fetch_data_from_pubmed(query):
    article_ids, total_results = send_pubmed_search_query(query)
    
    if total_results < 20:
        # Lade die Details und PDFs herunter
        studies = fetch_study_titles(article_ids)
        for study in studies:
            print(f"Studien-ID: {study['id']}, Titel: {study['title']}")
            download_pdf(study['id'])
    else:
        # Nur Titel anzeigen, keine PDFs herunterladen
        print(f"Suchanfrage '{query}' hat {total_results} Treffer. Lade Titel zur Analyse...")
        titles = fetch_study_titles(article_ids)
        for study in titles:
            print(f"Studien-ID: {study['id']}, Titel: {study['title']}")
        # Hier könntest du die Titel und Studien-ID in einem Verlauf speichern

# Beispielnutzung:
if __name__ == "__main__":
    query = "aspirin treatment AND chronic headache"
    fetch_data_from_pubmed(query)
