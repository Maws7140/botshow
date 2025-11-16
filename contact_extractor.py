"""
Contact information extraction module.
"""
import re
from typing import Optional, Dict
from bs4 import BeautifulSoup


class ContactExtractor:
    """Extracts contact information from HTML content."""

    @staticmethod
    def extract_phone(text: str) -> Optional[str]:
        """
        Extract phone number from text.
        Looks for international format with + prefix.
        """
        # Pattern for international phone numbers
        phone_pattern = r'\+\d{1,4}[\s\-]?\d{1,4}[\s\-]?\d{1,4}[\s\-]?\d{1,9}'
        match = re.search(phone_pattern, text)

        if match:
            # Clean up the phone number (remove spaces and dashes)
            phone = match.group(0)
            phone = re.sub(r'[\s\-]', '', phone)
            return phone

        return None

    @staticmethod
    def extract_email(text: str) -> Optional[str]:
        """Extract email address from text."""
        # Email pattern
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(email_pattern, text)

        if match:
            return match.group(0).lower()

        return None

    @staticmethod
    def is_valid_china_number(phone: str) -> bool:
        """Check if phone number starts with +86 (China country code)."""
        if not phone:
            return False
        return phone.startswith('+86')

    @staticmethod
    def extract_contact_info(html_content: str, selectors: Dict = None) -> Dict:
        """
        Extract all contact information from HTML content.

        Args:
            html_content: HTML content to parse
            selectors: Optional dict with CSS selectors for specific elements

        Returns:
            Dict with extracted contact information
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        # Default selectors (can be customized per marketplace)
        if selectors is None:
            selectors = {
                'contact_section': ['.contact-info', '.seller-info', '.vendor-info', '#contact'],
                'name': ['.seller-name', '.contact-name', '.vendor-name'],
                'business': ['.company-name', '.business-name', '.store-name'],
            }

        result = {
            'name': '',
            'business_info': '',
            'phone': '',
            'email': '',
            'is_china': False
        }

        # Try to find contact section
        contact_section = None
        for selector in selectors.get('contact_section', []):
            contact_section = soup.select_one(selector)
            if contact_section:
                break

        # If no specific section found, use the entire content
        if not contact_section:
            contact_section = soup

        # Get all text from contact section
        contact_text = contact_section.get_text(separator=' ', strip=True)

        # Extract phone
        phone = ContactExtractor.extract_phone(contact_text)
        if phone:
            result['phone'] = phone
            result['is_china'] = ContactExtractor.is_valid_china_number(phone)

        # Extract email
        email = ContactExtractor.extract_email(contact_text)
        if email:
            result['email'] = email

        # Extract name
        for selector in selectors.get('name', []):
            name_elem = contact_section.select_one(selector)
            if name_elem:
                result['name'] = name_elem.get_text(strip=True)
                break

        # Extract business info
        for selector in selectors.get('business', []):
            business_elem = contact_section.select_one(selector)
            if business_elem:
                result['business_info'] = business_elem.get_text(strip=True)
                break

        # If name or business still empty, try to extract from text
        if not result['name']:
            # Try to find a name pattern (capitalized words)
            lines = contact_text.split('\n')
            for line in lines[:5]:  # Check first 5 lines
                line = line.strip()
                if line and len(line.split()) <= 4 and line[0].isupper():
                    result['name'] = line
                    break

        return result

    @staticmethod
    def should_send_message(contact_info: Dict) -> bool:
        """
        Determine if a message should be sent based on contact info.

        Rules:
        - Phone must start with +86
        - Email must be present
        """
        return (
            contact_info.get('is_china', False) and
            contact_info.get('email', '') != ''
        )
