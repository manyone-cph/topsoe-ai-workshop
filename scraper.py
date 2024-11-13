import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import markdown
import time
from typing import Set, Dict, List

class TopsoeScraper:
    def __init__(self):
        self.base_url = "https://www.topsoe.com"
        self.visited_urls: Set[str] = set()
        self.main_sections = {
            "knowledge-insights": "Knowledge & Insights",
            "solutions": "Solutions",
            "news-media": "News & Media",
            "about": "About",
            "careers": "Careers",
            "investors": "Investors"
        }
        self.output_dir = "topsoe_content"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def create_folder_structure(self):
        """Create the initial folder structure"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # Create main section folders
        for section in self.main_sections.values():
            section_path = os.path.join(self.output_dir, section)
            if not os.path.exists(section_path):
                os.makedirs(section_path)

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

        # Determine the section and create folder path
        section = None
        for section_key, section_name in self.main_sections.items():
            if section_key in path_parts:
                section = section_name
                break

        if not section:
            section = "Other"

        # Create folder path
        folder_path = os.path.join(self.output_dir, section)
        for part in path_parts[1:-1]:  # Skip the section name and filename
            folder_path = os.path.join(folder_path, self.clean_filename(part))
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

        # Create markdown file
        filename = f"{self.clean_filename(title or path_parts[-1])}.md"
        file_path = os.path.join(folder_path, filename)

        # Save content with metadata
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"---\n")
            f.write(f"title: {title}\n")
            f.write(f"url: {url}\n")
            f.write(f"section: {section}\n")
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
        """Extract the main content from the page"""
        # Remove unwanted elements
        for element in soup.find_all(['script', 'style', 'nav', 'footer']):
            element.decompose()

        # Find main content area (adjust selectors based on Topsoe's HTML structure)
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
        
        if main_content:
            return main_content.get_text(strip=True)
        return soup.get_text(strip=True)

    def should_follow_link(self, url: str) -> bool:
        """Determine if a link should be followed"""
        if not url.startswith(self.base_url):
            return False
        
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.split('/')
        
        # Check if URL is in main sections
        return any(section in parsed_url.path for section in self.main_sections.keys())

    def start_scraping(self):
        """Start the scraping process"""
        self.create_folder_structure()
        urls_to_scrape = [self.base_url]

        while urls_to_scrape:
            url = urls_to_scrape.pop(0)
            new_urls = self.scrape_page(url)
            urls_to_scrape.extend([u for u in new_urls if u not in self.visited_urls])

def main():
    scraper = TopsoeScraper()
    scraper.start_scraping()

if __name__ == "__main__":
    main()