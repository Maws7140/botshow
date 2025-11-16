"""
Web scraping module for marketplace products.
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
from typing import List, Dict, Optional
from bs4 import BeautifulSoup


class MarketplaceScraper:
    """Scrapes product pages from marketplace websites."""

    def __init__(self, headless: bool = True, page_load_timeout: int = 30):
        """
        Initialize the web scraper.

        Args:
            headless: Run browser in headless mode
            page_load_timeout: Maximum time to wait for page loads
        """
        self.headless = headless
        self.page_load_timeout = page_load_timeout
        self.driver = None
        self._init_driver()

    def _init_driver(self):
        """Initialize the Selenium WebDriver."""
        chrome_options = Options()

        if self.headless:
            chrome_options.add_argument('--headless')

        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(self.page_load_timeout)
            print("✓ WebDriver initialized successfully")
        except Exception as e:
            print(f"✗ Failed to initialize WebDriver: {e}")
            raise

    def close(self):
        """Close the browser and clean up resources."""
        if self.driver:
            self.driver.quit()
            print("✓ Browser closed")

    def get_product_links(self, marketplace_url: str, max_pages: int = 10) -> List[str]:
        """
        Get all product links from marketplace pages.

        Args:
            marketplace_url: Base URL of the marketplace
            max_pages: Maximum number of pages to scrape

        Returns:
            List of product URLs
        """
        product_links = []

        try:
            for page_num in range(1, max_pages + 1):
                # Construct page URL (adjust based on marketplace structure)
                page_url = f"{marketplace_url}?page={page_num}"
                print(f"Scraping page {page_num}: {page_url}")

                self.driver.get(page_url)
                time.sleep(2)  # Wait for page to load

                # Find product links (adjust selectors based on marketplace)
                # Common selectors for product links
                selectors = [
                    'a.product-link',
                    'a[href*="/product/"]',
                    '.product-item a',
                    '.product-card a',
                    'a.item-link'
                ]

                page_source = self.driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')

                found_links = False
                for selector in selectors:
                    links = soup.select(selector)
                    if links:
                        for link in links:
                            href = link.get('href', '')
                            if href:
                                # Make absolute URL if needed
                                if href.startswith('/'):
                                    from urllib.parse import urljoin
                                    href = urljoin(marketplace_url, href)
                                if href not in product_links:
                                    product_links.append(href)
                        found_links = True
                        break

                if not found_links:
                    print(f"No products found on page {page_num}")
                    break

                print(f"Found {len(product_links)} total products so far")

        except Exception as e:
            print(f"Error scraping product links: {e}")

        return product_links

    def get_contact_page_html(self, product_url: str, contact_selectors: List[str] = None) -> Optional[str]:
        """
        Navigate to product page and extract contact information section.

        Args:
            product_url: URL of the product page
            contact_selectors: List of CSS selectors or button texts to find contact info

        Returns:
            HTML content of the contact section or None if not found
        """
        if contact_selectors is None:
            contact_selectors = [
                "//button[contains(text(), 'Contact')]",
                "//a[contains(text(), 'Contact')]",
                "//button[contains(text(), 'Seller')]",
                "//a[contains(text(), 'Seller')]",
                ".contact-seller",
                ".view-contact",
                "#contact-info"
            ]

        try:
            self.driver.get(product_url)
            time.sleep(2)  # Wait for initial page load

            # Try to find and click contact button/link
            contact_section_html = None

            for selector in contact_selectors:
                try:
                    if selector.startswith('//'):
                        # XPath selector
                        element = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        element.click()
                        time.sleep(2)  # Wait for contact info to load
                        contact_section_html = self.driver.page_source
                        break
                    else:
                        # CSS selector
                        element = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                        element.click()
                        time.sleep(2)
                        contact_section_html = self.driver.page_source
                        break
                except (TimeoutException, NoSuchElementException):
                    continue

            # If no button found, return entire page source
            if not contact_section_html:
                contact_section_html = self.driver.page_source

            return contact_section_html

        except Exception as e:
            print(f"Error getting contact page for {product_url}: {e}")
            return None

    def extract_price(self, html_content: str) -> Optional[float]:
        """
        Extract price from product page.

        Args:
            html_content: HTML content of the page

        Returns:
            Price as float or None if not found
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        # Common price selectors
        price_selectors = [
            '.price',
            '.product-price',
            '[class*="price"]',
            '[itemprop="price"]'
        ]

        for selector in price_selectors:
            price_elem = soup.select_one(selector)
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                # Extract numeric value
                import re
                price_match = re.search(r'[\d,]+\.?\d*', price_text)
                if price_match:
                    try:
                        price = float(price_match.group(0).replace(',', ''))
                        return price
                    except ValueError:
                        continue

        return None

    def extract_category(self, html_content: str) -> Optional[str]:
        """
        Extract category from product page.

        Args:
            html_content: HTML content of the page

        Returns:
            Category name or None if not found
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        # Common category selectors
        category_selectors = [
            '.breadcrumb a',
            '.category',
            '[itemprop="category"]',
            '.product-category'
        ]

        for selector in category_selectors:
            category_elem = soup.select_one(selector)
            if category_elem:
                return category_elem.get_text(strip=True).lower()

        return None
