#!/usr/bin/env python3
"""
Web scraper for Google Lens image descriptions
Fetches alt text and captions from matching image URLs
"""
import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urlparse
import json

class ImageDescriptionScraper:
    """Scrapes image descriptions from web pages"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def scrape_image_description(self, image_url: str, max_retries: int = 2) -> str:
        """Scrape description/caption/alt text for an image URL"""
        if not image_url:
            return None

        # Extract domain to handle different site structures
        domain = urlparse(image_url).netloc.lower()

        for attempt in range(max_retries):
            try:
                # Don't scrape YouTube (blocked) or obvious video sites
                if any(skip in domain for skip in ['youtube', 'youtu.be', 'vimeo', 'dailymotion']):
                    return None

                response = self.session.get(image_url, timeout=10)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, 'html.parser')

                # Try different strategies based on domain
                description = None

                if 'cnn.com' in domain:
                    description = self._scrape_cnn(soup, image_url)
                elif 'newsweek.com' in domain:
                    description = self._scrape_newsweek(soup, image_url)
                elif any(site in domain for site in ['reuters', 'apnews', 'bbc']):
                    description = self._scrape_news_site(soup, image_url)
                else:
                    description = self._scrape_generic(soup, image_url)

                if description and len(description.strip()) > 10:
                    return description.strip()

                # Rate limiting
                time.sleep(1)

            except Exception as e:
                print(f"Scraping error for {image_url}: {e}")
                time.sleep(2)

        return None

    def _scrape_cnn(self, soup, image_url):
        """Scrape CNN articles for image descriptions"""
        # Look for image captions
        captions = soup.find_all(['div', 'p', 'figcaption'], class_=re.compile(r'caption|image-caption|photo-caption'))
        for caption in captions:
            text = caption.get_text(strip=True)
            if text and len(text) > 20:
                return text

        # Look for alt text on images
        images = soup.find_all('img', alt=True)
        for img in images:
            alt_text = img.get('alt', '').strip()
            if alt_text and len(alt_text) > 15 and not alt_text.startswith(('http', 'data:')):
                return alt_text

        return None

    def _scrape_newsweek(self, soup, image_url):
        """Scrape Newsweek articles"""
        # Look for article content that might describe images
        content = soup.find('div', class_=re.compile(r'article|content|body'))
        if content:
            # Look for the first substantial paragraph
            paragraphs = content.find_all('p')
            for p in paragraphs[:3]:  # Check first 3 paragraphs
                text = p.get_text(strip=True)
                if text and len(text) > 50:
                    return text[:200] + '...' if len(text) > 200 else text

        return self._scrape_generic(soup, image_url)

    def _scrape_news_site(self, soup, image_url):
        """Scrape general news sites"""
        # Look for figure captions
        figures = soup.find_all('figure')
        for figure in figures:
            figcaption = figure.find('figcaption')
            if figcaption:
                text = figcaption.get_text(strip=True)
                if text and len(text) > 15:
                    return text

        # Look for structured data (JSON-LD)
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    # Look for image descriptions in structured data
                    if 'description' in data:
                        desc = data['description']
                        if isinstance(desc, str) and len(desc) > 20:
                            return desc
            except:
                continue

        return self._scrape_generic(soup, image_url)

    def _scrape_generic(self, soup, image_url):
        """Generic scraping for any website"""
        # Look for alt text on images near the target image URL
        target_filename = image_url.split('/')[-1].split('?')[0]

        images = soup.find_all('img', alt=True)
        for img in images:
            alt_text = img.get('alt', '').strip()
            if alt_text and len(alt_text) > 15 and not alt_text.startswith(('http', 'data:')):
                # Check if this might be related to our image
                img_src = img.get('src', '')
                if target_filename in img_src or any(keyword in alt_text.lower() for keyword in ['submarine', 'soldier', 'military', 'navy']):
                    return alt_text

        # Look for meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            content = meta_desc['content'].strip()
            if len(content) > 30:
                return content[:150] + '...' if len(content) > 150 else content

        # Look for Open Graph description
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            content = og_desc['content'].strip()
            if len(content) > 30:
                return content[:150] + '...' if len(content) > 150 else content

        return None

def test_scraper():
    """Test the web scraper on known page URLs"""
    scraper = ImageDescriptionScraper()

    # Test with working URLs
    test_urls = [
        "https://en.wikipedia.org/wiki/Submarine",  # Wikipedia has good alt text
        "https://en.wikipedia.org/wiki/Soldier",    # Another test
        "https://www.bbc.com/news"  # News site
    ]

    for url in test_urls:
        print(f"\nTesting page URL: {url}")
        description = scraper.scrape_image_description(url)
        if description:
            print(f"Found description: {description}")
        else:
            print("No description found")

if __name__ == "__main__":
    test_scraper()
