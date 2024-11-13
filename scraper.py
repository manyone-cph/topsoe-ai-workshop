import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from typing import Set, List

class Scraper:
    def __init__(self):
        self.base_url = "https://www.topsoe.com"
        self.visited_urls: Set[str] = set()
        self.output_dir = "topsoe_scrape"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def clean_filename(self, filename: str) -> str:
        """Convert URL or title to valid filename"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '-')
        return filename.strip()

    def save_page_content(self, url: str, content: str, title: str) -> None:
        """Save page content as markdown file in appropriate folder"""
        parsed_url = urlparse(url)
        path_parts = [p for p in parsed_url.path.split('/') if p]

        # Handle root URL
        if not path_parts:
            folder_path = self.output_dir
            filename = "index.md"
        else:
            # Create folder path based on URL structure
            folder_path = self.output_dir
            for part in path_parts[:-1]:  # All parts except the last one
                folder_path = os.path.join(folder_path, self.clean_filename(part))
            
            # Use last part of path or 'index' for filename
            filename = f"{self.clean_filename(path_parts[-1] or 'index')}.md"

        # Create all necessary directories
        os.makedirs(folder_path, exist_ok=True)

        # Create full file path
        file_path = os.path.join(folder_path, filename)

        # Save content with metadata
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"---\n")
            f.write(f"title: {title}\n")
            f.write(f"url: {url}\n")
            f.write(f"---\n\n")
            f.write(content)

    def scrape_page(self, url: str) -> List[str]:
        """Scrape a single page and return found links"""
        if url in self.visited_urls:
            return []

        self.visited_urls.add(url)
        print(f"Scraping: {url}")

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract content
            title = soup.title.string if soup.title else ""
            content = self.extract_main_content(soup)
            
            # Save the content
            self.save_page_content(url, content, title)

            # Find all links
            links = []
            for a in soup.find_all('a', href=True):
                href = urljoin(url, a['href'])
                if self.should_follow_link(href):
                    links.append(href)

            time.sleep(1)  # Respect the website
            return links

        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return []

    def extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract and structure the main content from the page"""
        # Remove unwanted elements
        for element in soup.find_all(['script', 'style', 'nav', 'footer', 'form', 'aside', 'comments']):
            element.decompose()

        # Try to find the main article content
        article = soup.find('article') or soup.find('main') or soup.find('div', class_='content')
        
        if not article:
            return ""

        content_parts = []
        
        # Extract title
        title = soup.find('h1')
        if title:
            content_parts.append(f"# {title.get_text().strip()}\n")

        # Extract date if available
        date = soup.find('time') or soup.find(class_=['date', 'published', 'post-date'])
        if date:
            content_parts.append(f"*Published: {date.get_text().strip()}*\n")

        def process_text_styling(element):
            """Process inline text styling recursively"""
            if isinstance(element, str):
                return element.strip()
            
            if hasattr(element, 'contents'):
                text = ''
                for child in element.contents:
                    if isinstance(child, str):
                        text += child.strip()
                    else:
                        # Handle nested elements
                        child_text = process_text_styling(child)
                        if child.name in ['strong', 'b']:
                            text += f"**{child_text}**"
                        elif child.name in ['em', 'i']:
                            text += f"*{child_text}*"
                        elif child.name == 'a':
                            href = child.get('href', '')
                            text += f"[{child_text}]({href})"
                        else:
                            text += child_text
                return text
            return ''

        # Extract main content with proper formatting
        for element in article.find_all(['p', 'h2', 'h3', 'h4', 'ul', 'ol', 'blockquote']):
            if element.parent.name in ['aside', 'nav', 'footer']:
                continue
            
            if element.name in ['ul', 'ol']:
                items = []
                for li in element.find_all('li'):
                    item_text = process_text_styling(li)
                    items.append(f"- {item_text}")
                content_parts.append("\n" + "\n".join(items) + "\n")
            else:
                text = process_text_styling(element)
                if text:
                    if element.name == 'h2':
                        content_parts.append(f"\n## {text}\n")
                    elif element.name == 'h3':
                        content_parts.append(f"\n### {text}\n")
                    elif element.name == 'h4':
                        content_parts.append(f"\n#### {text}\n")
                    elif element.name == 'blockquote':
                        content_parts.append(f"\n> {text}\n")
                    else:  # paragraphs
                        content_parts.append(f"\n{text}\n")

        # Join all parts and clean up spacing
        content = "\n".join(content_parts)
        
        # Clean up excessive newlines while preserving paragraph breaks
        content = "\n\n".join(para.strip() for para in content.split('\n\n') if para.strip())
        
        return content

    def should_follow_link(self, url: str) -> bool:
        """Determine if a link should be followed"""
        if not url.startswith(self.base_url):
            return False
        
        parsed_url = urlparse(url)
        
        # Skip certain paths that aren't articles
        skip_paths = [
            '/search', 
            '/login',
            '/contact',
            '/sitemap',
            '/tags',
            '/categories'
        ]
        
        if any(path in parsed_url.path for path in skip_paths):
            return False
        
        # Skip URLs with query parameters
        if parsed_url.query:
            return False
        
        return True

    def start_scraping(self):
        """Start the scraping process"""
        # Create base output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        urls_to_scrape = [self.base_url]

        while urls_to_scrape:
            url = urls_to_scrape.pop(0)
            new_urls = self.scrape_page(url)
            urls_to_scrape.extend([u for u in new_urls if u not in self.visited_urls])

def main():
    scraper = Scraper()
    scraper.start_scraping()

if __name__ == "__main__":
    main()