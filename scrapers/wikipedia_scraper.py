import wikipediaapi
import json
import os
from datetime import datetime


class WikipediaScraper:
    def __init__(self, language='en'):
        self.wiki = wikipediaapi.Wikipedia(
            user_agent='SierraLeoneAI/1.0 (Educational Project)',
            language=language
        )

    def get_page_content(self, title):
        """Get full content of a Wikipedia page"""
        page = self.wiki.page(title)

        if not page.exists():
            print(f"❌ Page not found: {title}")
            return None

        return {
            'title': page.title,
            'content': page.text,
            'url': page.fullurl,
            'summary': page.summary,
            'categories': list(page.categories.keys()),
            'scraped_at': datetime.now().isoformat()
        }

    def scrape_sierra_leone_topics(self):
        """Scrape all major Sierra Leone topics"""

        # Categorized topics to scrape
        topics = {
            'history': [
                'Sierra_Leone',
                'History_of_Sierra_Leone',
                'Sierra_Leone_Civil_War',
                'Freetown',
                'British_Sierra_Leone',
                'Sierra_Leone_Colony_and_Protectorate',
                'Independence_of_Sierra_Leone',
                'Truth_and_Reconciliation_Commission_(Sierra_Leone)',
                'Special_Court_for_Sierra_Leone',
                'Revolutionary_United_Front',
            ],
            'culture': [
                'Culture_of_Sierra_Leone',
                'Krio_language',
                'Krio_people',
                'Mende_people',
                'Temne_people',
                'Limba_people_(Sierra_Leone)',
                'Music_of_Sierra_Leone',
                'Sierra_Leone_Creole_people',
                'Religion_in_Sierra_Leone',
                'Education_in_Sierra_Leone',
            ],
            'politics': [
                'Politics_of_Sierra_Leone',
                'Government_of_Sierra_Leone',
                'President_of_Sierra_Leone',
                'Parliament_of_Sierra_Leone',
                'All_People\'s_Congress',
                'Sierra_Leone_People\'s_Party',
                'Elections_in_Sierra_Leone',
                'Paramount_chief',
                'Chiefdoms_of_Sierra_Leone',
                'Julius_Maada_Bio',
            ],
            'economy': [
                'Economy_of_Sierra_Leone',
                'Mining_industry_of_Sierra_Leone',
                'Agriculture_in_Sierra_Leone',
                'Transport_in_Sierra_Leone',
                'Telecommunications_in_Sierra_Leone',
                'Tourism_in_Sierra_Leone',
                'Banking_in_Sierra_Leone',
                'Sierra_Leonean_leone',
            ],
            'general': [
                'Geography_of_Sierra_Leone',
                'Provinces_of_Sierra_Leone',
                'Bo,_Sierra_Leone',
                'Kenema',
                'Makeni',
                'Koidu',
                'Demographics_of_Sierra_Leone',
                'Health_in_Sierra_Leone',
                'COVID-19_pandemic_in_Sierra_Leone',
                'Ebola_virus_epidemic_in_Sierra_Leone',
                'Kush',
            ]
        }

        all_articles = {}

        for category, page_titles in topics.items():
            print(f"\n📚 Scraping {category.upper()} articles...")
            articles = []

            for title in page_titles:
                print(f"  Fetching: {title}")
                article = self.get_page_content(title)

                if article:
                    articles.append(article)
                    print(f"  ✅ Success: {len(article['content'])} characters")
                else:
                    print(f"  ⚠️  Skipped: {title}")

            all_articles[category] = articles
            print(f"✅ Collected {len(articles)} {category} articles")

        return all_articles

    def save_to_files(self, articles_by_category, base_dir='data'):
        """Save scraped articles to organized files"""

        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        for category, articles in articles_by_category.items():
            category_dir = os.path.join(base_dir, category)
            os.makedirs(category_dir, exist_ok=True)

            # Save as individual text files
            for article in articles:
                # Clean filename
                filename = article['title'].replace(' ', '_').replace('/', '_') + '.txt'
                filepath = os.path.join(category_dir, filename)

                # Write content
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"Title: {article['title']}\n")
                    f.write(f"URL: {article['url']}\n")
                    f.write(f"Scraped: {article['scraped_at']}\n")
                    f.write(f"\n{'=' * 80}\n\n")
                    f.write(article['content'])

            # Also save as JSON for metadata
            json_path = os.path.join(category_dir, f'{category}_metadata.json')
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(articles, f, indent=2, ensure_ascii=False)

            print(f"💾 Saved {len(articles)} articles to {category_dir}/")


def main():
    print("=" * 80)
    print("🇸🇱 SIERRA LEONE WIKIPEDIA SCRAPER")
    print("=" * 80)

    scraper = WikipediaScraper()

    print("\n🔍 Starting to scrape Wikipedia articles...")
    articles = scraper.scrape_sierra_leone_topics()

    print("\n💾 Saving articles to files...")
    scraper.save_to_files(articles)

    # Summary
    total_articles = sum(len(articles) for articles in articles.values())
    print("\n" + "=" * 80)
    print(f"✅ SCRAPING COMPLETE!")
    print(f"   Total articles collected: {total_articles}")
    print(f"   Categories: {len(articles)}")
    for category, arts in articles.items():
        print(f"   - {category}: {len(arts)} articles")
    print("=" * 80)


if __name__ == "__main__":
    main()