import requests
from bs4 import BeautifulSoup
from newspaper import Article
import os
import re
from datetime import datetime
import time
from urllib.parse import urlparse


class LinksScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def parse_links_file(self, links_file='data/links.txt'):
        """Parse the links.txt file and return categorized URLs"""
        if not os.path.exists(links_file):
            print(f"⚠️  Links file not found: {links_file}")
            return {}

        links_by_category = {}
        current_category = None

        try:
            with open(links_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Check for category header [category]
                    if line.startswith('[') and line.endswith(']'):
                        current_category = line[1:-1].strip()
                        if current_category not in links_by_category:
                            links_by_category[current_category] = []
                        continue
                    
                    # Add URL to current category
                    if current_category and line.startswith('http'):
                        links_by_category[current_category].append(line)
                    elif current_category and line:
                        # Handle URLs without http prefix
                        if not line.startswith('http'):
                            line = 'https://' + line
                        links_by_category[current_category].append(line)

        except Exception as e:
            print(f"❌ Error parsing links file: {str(e)}")
            return {}

        return links_by_category

    def scrape_url_content(self, url):
        """Scrape content from a single URL using newspaper3k with fallback"""
        try:
            # Try newspaper3k first
            article = Article(url)
            article.download()
            article.parse()
            
            if article.text and len(article.text.strip()) > 100:
                return {
                    'title': article.title or self._extract_title_from_url(url),
                    'content': article.text,
                    'url': url,
                    'publish_date': str(article.publish_date) if article.publish_date else None,
                    'authors': article.authors,
                    'scraped_at': datetime.now().isoformat(),
                    'method': 'newspaper3k'
                }
        except Exception as e:
            print(f"  ⚠️  Newspaper3k failed for {url}: {str(e)}")

        # Fallback to requests + BeautifulSoup
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else self._extract_title_from_url(url)
            
            # Extract main content
            content = soup.get_text()
            lines = (line.strip() for line in content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            if len(text) > 100:
                return {
                    'title': title_text,
                    'content': text,
                    'url': url,
                    'publish_date': None,
                    'authors': [],
                    'scraped_at': datetime.now().isoformat(),
                    'method': 'beautifulsoup'
                }
                
        except Exception as e:
            print(f"  ❌ BeautifulSoup fallback failed for {url}: {str(e)}")

        return None

    def _extract_title_from_url(self, url):
        """Extract a readable title from URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.replace('www.', '')
            path = parsed.path.strip('/').replace('/', ' - ')
            if path:
                return f"{domain} - {path}"
            return domain
        except:
            return url

    def scrape_links_from_file(self, links_file='data/links.txt', base_dir='data'):
        """Scrape all URLs from links.txt file and save to category folders"""
        
        print("\n" + "=" * 80)
        print("🔗 PROCESSING LINKS FROM FILE")
        print("=" * 80)
        
        # Parse links file
        links_by_category = self.parse_links_file(links_file)
        
        if not links_by_category:
            print("⚠️  No links found in links file")
            return {}
        
        print(f"📋 Found links in {len(links_by_category)} categories:")
        for category, urls in links_by_category.items():
            print(f"   - {category}: {len(urls)} URLs")
        
        all_scraped_articles = {}
        
        for category, urls in links_by_category.items():
            if not urls:
                continue
                
            print(f"\n🔗 Processing {category.upper()} links...")
            articles = []
            
            for i, url in enumerate(urls, 1):
                print(f"   [{i}/{len(urls)}] Scraping: {url[:60]}...")
                
                article = self.scrape_url_content(url)
                if article:
                    articles.append(article)
                    print(f"   ✅ Success: {len(article['content'])} characters ({article['method']})")
                else:
                    print(f"   ❌ Failed to scrape content")
                
                # Be respectful to servers
                time.sleep(1)
            
            all_scraped_articles[category] = articles
            print(f"✅ Collected {len(articles)} articles from {category}")
        
        # Save articles to files
        self.save_links_to_files(all_scraped_articles, base_dir)
        
        return all_scraped_articles

    def save_links_to_files(self, articles_by_category, base_dir='data'):
        """Save scraped link articles to category folders"""
        
        print(f"\n💾 Saving link articles to category folders...")
        
        for category, articles in articles_by_category.items():
            if not articles:
                continue
                
            category_dir = os.path.join(base_dir, category)
            os.makedirs(category_dir, exist_ok=True)
            
            for i, article in enumerate(articles, 1):
                # Create safe filename
                title_slug = article['title'][:50].replace(' ', '_').replace('/', '_')
                title_slug = re.sub(r'[^\w\-_]', '', title_slug)  # Remove special chars
                filename = f"link_{i}_{title_slug}.txt"
                filepath = os.path.join(category_dir, filename)
                
                # Write content
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"Title: {article['title']}\n")
                    f.write(f"Source: links\n")
                    f.write(f"URL: {article['url']}\n")
                    f.write(f"Date: {article['publish_date'] or 'Unknown'}\n")
                    f.write(f"Scraped: {article['scraped_at']}\n")
                    f.write(f"Method: {article['method']}\n")
                    f.write(f"\n{'=' * 80}\n\n")
                    f.write(article['content'])
                
                print(f"  💾 Saved: {filename}")
            
            print(f"✅ Saved {len(articles)} link articles to {category_dir}/")


def main():
    print("=" * 80)
    print("🇸🇱 SIERRA LEONE LINKS SCRAPER")
    print("=" * 80)
    print("\nThis scraper processes URLs from data/links.txt")
    print("and saves them as text files in appropriate category folders.\n")
    
    scraper = LinksScraper()
    
    print("🔍 Starting to scrape links from file...")
    articles = scraper.scrape_links_from_file()
    
    # Summary
    total_articles = sum(len(arts) for arts in articles.values())
    print("\n" + "=" * 80)
    print(f"✅ LINKS SCRAPING COMPLETE!")
    print(f"   Total articles collected: {total_articles}")
    for category, arts in articles.items():
        print(f"   - {category}: {len(arts)} articles")
    print("\n🚀 Next step: Run 'python data_loading.py' to create vector stores")
    print("=" * 80)


if __name__ == "__main__":
    main()
