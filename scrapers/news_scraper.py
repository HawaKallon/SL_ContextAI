import requests
from bs4 import BeautifulSoup
from newspaper import Article
import json
import os
from datetime import datetime
import time


class SierraLeoneNewsScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        # Sierra Leone news websites
        self.news_sources = {
            'awoko': 'https://awoko.org',
            'concord_times': 'https://concordtimes.com',
            'sierra_express': 'https://www.sierraexpressmedia.com',
            'ayv_news': 'https://ayvnews.com/',
            'calabash_newspaper': 'https://thecalabashnewspaper.com/',
            # 'sierralii': 'https://sierralii.gov.sl/'
        }

    def scrape_article_with_newspaper(self, url):
        """Use newspaper3k to extract article content"""
        try:
            article = Article(url)
            article.download()
            article.parse()

            return {
                'title': article.title,
                'content': article.text,
                'url': url,
                'publish_date': str(article.publish_date) if article.publish_date else None,
                'authors': article.authors,
                'scraped_at': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"  ❌ Error scraping {url}: {str(e)}")
            return None

    def get_article_links_from_homepage(self, source_name, url, max_links=10):
        """Scrape article links from homepage"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all article links (adjust selectors based on site structure)
            links = []
            for link in soup.find_all('a', href=True):
                href = link['href']

                # Make absolute URL
                if href.startswith('/'):
                    href = url + href
                elif not href.startswith('http'):
                    continue

                # Filter for article URLs (basic heuristic)
                if any(keyword in href.lower() for keyword in ['article', 'news', '202']):
                    if href not in links:
                        links.append(href)

                if len(links) >= max_links:
                    break

            return links

        except Exception as e:
            print(f"  ❌ Error getting links from {source_name}: {str(e)}")
            return []

    def scrape_news_sources(self, articles_per_source=10):
        """Scrape articles from all news sources"""

        all_articles = {}

        for source_name, source_url in self.news_sources.items():
            print(f"\n📰 Scraping {source_name}...")
            print(f"   URL: {source_url}")

            # Get article links
            article_links = self.get_article_links_from_homepage(
                source_name,
                source_url,
                max_links=articles_per_source
            )

            print(f"   Found {len(article_links)} article links")

            # Scrape each article
            articles = []
            for i, link in enumerate(article_links, 1):
                print(f"   [{i}/{len(article_links)}] Scraping: {link[:60]}...")

                article = self.scrape_article_with_newspaper(link)
                if article and article['content']:
                    articles.append(article)
                    print(f"   ✅ Success: {len(article['content'])} characters")

                time.sleep(1)  # Be respectful to servers

            all_articles[source_name] = articles
            print(f"✅ Collected {len(articles)} articles from {source_name}")

        return all_articles

    def save_to_files(self, articles_by_source, base_dir='data/general'):
        """Save scraped news articles"""

        os.makedirs(base_dir, exist_ok=True)

        for source, articles in articles_by_source.items():
            for i, article in enumerate(articles, 1):
                # Create safe filename
                title_slug = article['title'][:50].replace(' ', '_').replace('/', '_')
                filename = f"{source}_{i}_{title_slug}.txt"
                filepath = os.path.join(base_dir, filename)

                # Write content
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"Title: {article['title']}\n")
                    f.write(f"Source: {source}\n")
                    f.write(f"URL: {article['url']}\n")
                    f.write(f"Date: {article['publish_date']}\n")
                    f.write(f"\n{'=' * 80}\n\n")
                    f.write(article['content'])

            print(f"💾 Saved {len(articles)} articles from {source}")


def main():
    print("=" * 80)
    print("🇸🇱 SIERRA LEONE NEWS SCRAPER")
    print("=" * 80)
    print("\n⚠️  Note: This scraper may take time and depends on website structure")
    print("⚠️  Some sites may block scrapers. Be respectful of rate limits.\n")

    scraper = SierraLeoneNewsScraper()

    print("🔍 Starting to scrape news articles...")
    articles = scraper.scrape_news_sources(articles_per_source=5)  # Start with 5 per source

    print("\n💾 Saving articles to files...")
    scraper.save_to_files(articles)

    # Summary
    total_articles = sum(len(arts) for arts in articles.values())
    print("\n" + "=" * 80)
    print(f"✅ SCRAPING COMPLETE!")
    print(f"   Total articles collected: {total_articles}")
    for source, arts in articles.items():
        print(f"   - {source}: {len(arts)} articles")
    print("=" * 80)


if __name__ == "__main__":
    main()