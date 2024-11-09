from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Функція для пошуку статей з PubMed через ESearch
def search_pubmed(query, api_key):
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    search_params = {
        "db": "pubmed",
        "term": query,
        "usehistory": "y",
        "retmode": "json",
        "retmax": 3,  # Клькість результатів пошуку
        "api_key": api_key
    }
    search_response = requests.get(search_url, params=search_params)
    if search_response.status_code != 200:
        return None, {"error": "Error in search request", "details": search_response.text}
    try:
        search_data = search_response.json()
        query_key = search_data['esearchresult'].get('querykey')
        web_env = search_data['esearchresult'].get('webenv')
        if not query_key or not web_env:
            return None, {"error": "No results found for the query"}
        return {"query_key": query_key, "web_env": web_env}, None
    except ValueError:
        return None, {"error": "Failed to parse JSON from search response", "details": search_response.text}

# Функція для отримання коротких змістів статей з PubMed через EFetch
def fetch_abstracts(query_key, web_env, api_key):
    fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    fetch_params = {
        "db": "pubmed",
        "query_key": query_key,
        "WebEnv": web_env,
        "rettype": "abstract",  # Тип: абстракт (короткий зміст)
        "retmode": "text",
        "api_key": api_key
    }
    fetch_response = requests.get(fetch_url, params=fetch_params)
    if fetch_response.status_code != 200:
        return None, {"error": "Error in fetch request", "details": fetch_response.text}
    
    try:
        abstracts = fetch_response.text
        return abstracts, None
    except ValueError:
        return None, {"error": "Failed to parse text from fetch response", "details": fetch_response.text}

# Основний ендпоінт для запиту анотацій з PubMed
@app.route('/get_pubmed_summaries', methods=['GET'])
def get_pubmed_summaries():
    query = request.args.get('query')
    api_key = os.getenv("PUBMED_API_KEY")  # Використовуємо змінну середовища

    # Перший запит для пошуку статей
    search_result, error = search_pubmed(query, api_key)
    if error:
        return jsonify(error), 500

    # Другий запит для отримання коротких змістів через EFetch
    abstracts, error = fetch_abstracts(search_result["query_key"], search_result["web_env"], api_key)
    if error:
        return jsonify(error), 500

    return jsonify({"abstracts": abstracts})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
