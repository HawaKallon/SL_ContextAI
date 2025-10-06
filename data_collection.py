"""
Main data collection orchestrator
Runs all scrapers and organizes data
"""

import os
import sys

# Add scrapers to path
sys.path.append('scrapers')

from scrapers.wikipedia_scraper import WikipediaScraper
from scrapers.news_scraper import SierraLeoneNewsScraper
from scrapers.links_scraper import LinksScraper


def collect_all_data():
    """Run all data collection scripts"""

    print("=" * 80)
    print("🇸🇱 SIERRA LEONE AI - COMPREHENSIVE DATA COLLECTION")
    print("=" * 80)
    print("\nThis will collect data from multiple sources:")
    print("  1. Links from data/links.txt file")
    print("  2. Wikipedia articles (history, culture, politics, economy)")
    print("  3. Sierra Leone news websites")
    print("\n⏱️  This may take 10-30 minutes depending on your internet speed")
    print("=" * 80)

    input("\nPress Enter to start data collection...")

    # Step 1: Links from links.txt
    print("\n\n" + "=" * 80)
    print("STEP 1: LINKS SCRAPING")
    print("=" * 80)

    links_scraper = LinksScraper()
    links_articles = links_scraper.scrape_links_from_file()

    # Step 2: Wikipedia
    print("\n\n" + "=" * 80)
    print("STEP 2: WIKIPEDIA SCRAPING")
    print("=" * 80)

    wiki_scraper = WikipediaScraper()
    wiki_articles = wiki_scraper.scrape_sierra_leone_topics()
    wiki_scraper.save_to_files(wiki_articles)

    # Step 3: News
    print("\n\n" + "=" * 80)
    print("STEP 3: NEWS SCRAPING")
    print("=" * 80)

    news_scraper = SierraLeoneNewsScraper()
    news_articles = news_scraper.scrape_news_sources(articles_per_source=5)
    news_scraper.save_to_files(news_articles)

    # Summary
    links_total = sum(len(articles) for articles in links_articles.values())
    wiki_total = sum(len(articles) for articles in wiki_articles.values())
    news_total = sum(len(articles) for articles in news_articles.values())

    print("\n\n" + "=" * 80)
    print("✅ DATA COLLECTION COMPLETE!")
    print("=" * 80)
    print(f"\n📊 Summary:")
    print(f"   Links articles: {links_total}")
    print(f"   Wikipedia articles: {wiki_total}")
    print(f"   News articles: {news_total}")
    print(f"   Total documents: {links_total + wiki_total + news_total}")
    print(f"\n📁 Data saved in:")
    print(f"   - data/history/")
    print(f"   - data/culture/")
    print(f"   - data/politics/")
    print(f"   - data/economy/")
    print(f"   - data/general/")
    print("\n🚀 Next step: Run 'python data_loading.py' to create vector stores")
    print("=" * 80)


if __name__ == "__main__":
    collect_all_data()