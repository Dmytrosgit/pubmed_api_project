from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

def search_pubmed(query, api_key):
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    search_params = {
        "db": "pubmed",
        "term": query,
        "usehistory": "y",
        "retmode": "json",
        "retmax": 10,  # Збільшуємо кількість результатів пошуку
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

def fetch_summaries(query_key, web_env, api_key):
    summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    summary_params = {
        "db": "pubmed",
        "query_key": query_key,
        "WebEnv": web_env,
        "retmax": 5,  # Можна налаштувати на більшу кількість, якщо потрібно
        "retmode": "json",
        "api_key": api_key
    }
    summary_response = requests.get(summary_url, params=summary_params)
    if summary_response.status_code != 200:
        return None, {"error": "Error in summary request", "details": summary_response.text}
    try:
        summaries = summary_response.json()
        return summaries, None
    except ValueError:
        return None, {"error": "Failed to parse JSON from summary response", "details": summary_response.text}

@app.route('/get_pubmed_summaries', methods=['GET'])
def get_pubmed_summaries():
    query = request.args.get('query')
    api_key = os.getenv("PUBMED_API_KEY")  # Використовуємо змінну середовища

    # Перший запит для пошуку статей
    search_result, error = search_pubmed(query, api_key)
    if error:
        return jsonify(error), 500

    # Другий запит для отримання анотацій
    summaries, error = fetch_summaries(search_result["query_key"], search_result["web_env"], api_key)
    if error:
        return jsonify(error), 500

    return jsonify(summaries)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
