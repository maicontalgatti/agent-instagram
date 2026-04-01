from newsapi import NewsApiClient

from config import NEWS_API_KEY
from safe_log import safe_exc

class NewsFetcher:
    def __init__(self):
        self.newsapi = NewsApiClient(api_key=NEWS_API_KEY)

    def fetch_tech_news(self, query='technology OR "software development"', language='pt', page_size=5):
        try:
            top_headlines = self.newsapi.get_everything(
                q=query,
                language=language,
                sort_by='relevancy',
                page_size=page_size
            )
            articles = top_headlines.get('articles', [])
            return articles
        except Exception as e:
            print(f"Erro ao buscar notícias: {safe_exc(e)}")
            return []

if __name__ == '__main__':
    fetcher = NewsFetcher()
    news = fetcher.fetch_tech_news()
    if news:
        for i, article in enumerate(news):
            print(f"\n--- Artigo {i+1} ---")
            print(f"Título: {article['title']}")
            print(f"Fonte: {article['source']['name']}")
            print(f"URL: {article['url']}")
            print(f"Descrição: {article['description']}")
    else:
        print("Nenhuma notícia encontrada.")
