from flask import Flask, request, jsonify
import requests

app = Flask(__name__)  # Це визначає додаток

@app.route('/get_pubmed_summaries', methods=['GET'])
def get_pubmed_summaries():
    query = request.args.get('query')
    api_key = "5ce7485e546a830055ece8fbacdc9f0dc709"  # Замініть на свій реальний API ключ

    # Перший запит для пошуку статей
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    search_params = {
        "db": "pubmed",
        "term": query,
        "usehistory": "y",
        "retmode": "json",  # Додаємо цей параметр
        "api_key": api_key
    }
    search_response = requests.get(search_url, params=search_params)

    # Перевірка на успішність запиту
    if search_response.status_code != 200:
        return jsonify({"error": "Error in search request", "details": search_response.text}), 500

    try:
        search_data = search_response.json()
        query_key = search_data['esearchresult']['querykey']
        web_env = search_data['esearchresult']['webenv']
    except ValueError:
        return jsonify({"error": "Failed to parse JSON from search response", "details": search_response.text}), 500

    # Другий запит для отримання анотацій
    summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    summary_params = {
        "db": "pubmed",
        "query_key": query_key,
        "WebEnv": web_env,
        "retmax": 5,
        "retmode": "json",  # Додаємо цей параметр
        "api_key": api_key
    }
    summary_response = requests.get(summary_url, params=summary_params)

    # Перевірка на успішність запиту
    if summary_response.status_code != 200:
        return jsonify({"error": "Error in summary request", "details": summary_response.text}), 500

    try:
        summaries = summary_response.json()
        return jsonify(summaries)
    except ValueError:
        return jsonify({"error": "Failed to parse JSON from summary response", "details": summary_response.text}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)