from newsapi import NewsApiClient

from config import NEWS_API_KEY
from safe_log import safe_exc

KEYWORDS = [
    "AI",
    "inteligência artificial",
    "OpenAI",
    "Google",
    "Apple",
    "Microsoft",
    "startup",
    "tecnologia",
    "inovação",
]


def _article_text(article: dict) -> str:
    title = article.get("title") or ""
    desc = article.get("description") or ""
    return f"{title} {desc}".lower()


def is_relevant(article: dict) -> bool:
    text = _article_text(article)
    return any(k.lower() in text for k in KEYWORDS)


def filter_relevant_articles(articles: list) -> list:
    return [a for a in articles if is_relevant(a)]


def impact_score(article: dict) -> int:
    title = (article.get("title") or "").lower()
    score = 0
    if "ai" in title:
        score += 3
    if "openai" in title:
        score += 3
    if "google" in title:
        score += 2
    if "lança" in title or "launch" in title:
        score += 2
    if "novo" in title:
        score += 1
    return score


def pick_best_article(articles: list) -> dict | None:
    if not articles:
        return None
    return sorted(articles, key=impact_score, reverse=True)[0]


class NewsFetcher:
    def __init__(self):
        self.newsapi = NewsApiClient(api_key=NEWS_API_KEY)

    def fetch_tech_news(self, query='technology OR "software development"', language='pt', page_size=30):
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
    news = filter_relevant_articles(news)
    if news:
        best = pick_best_article(news)
        print(f"Melhor notícia: {best['title']}")
        for i, article in enumerate(news):
            print(f"\n--- Artigo {i+1} ---")
            print(f"Título: {article['title']}")
            print(f"Fonte: {article['source']['name']}")
            print(f"URL: {article['url']}")
            print(f"Descrição: {article['description']}")
    else:
        print("Nenhuma notícia encontrada.")
