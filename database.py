"""
Database module for tracking contacted vendors.
"""
import sqlite3
from datetime import datetime
from typing import Optional, Dict, List
import threading


class ContactDatabase:
    """Database manager for tracking contacted vendors."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        """Initialize the database schema."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    phone TEXT,
                    name TEXT,
                    business_info TEXT,
                    product_url TEXT,
                    contacted_at TIMESTAMP,
                    message_sent BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_email ON contacts(email)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_phone ON contacts(phone)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_message_sent ON contacts(message_sent)
            ''')

            conn.commit()
            conn.close()

    def is_contacted(self, email: str) -> bool:
        """Check if a contact has already been messaged."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                'SELECT message_sent FROM contacts WHERE email = ?',
                (email,)
            )

            result = cursor.fetchone()
            conn.close()

            return result is not None and result[0] == 1

    def get_contact_by_email(self, email: str) -> Optional[Dict]:
        """Get contact information by email."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                'SELECT email, phone, name, business_info, message_sent FROM contacts WHERE email = ?',
                (email,)
            )

            result = cursor.fetchone()
            conn.close()

            if result:
                return {
                    'email': result[0],
                    'phone': result[1],
                    'name': result[2],
                    'business_info': result[3],
                    'message_sent': result[4]
                }
            return None

    def add_contact(self, email: str, phone: str, name: str = '',
                    business_info: str = '', product_url: str = '') -> bool:
        """Add a new contact to the database."""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT OR IGNORE INTO contacts
                    (email, phone, name, business_info, product_url)
                    VALUES (?, ?, ?, ?, ?)
                ''', (email, phone, name, business_info, product_url))

                conn.commit()
                conn.close()
                return True
            except Exception as e:
                print(f"Error adding contact: {e}")
                return False

    def mark_as_contacted(self, email: str) -> bool:
        """Mark a contact as messaged."""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute('''
                    UPDATE contacts
                    SET message_sent = 1, contacted_at = ?
                    WHERE email = ?
                ''', (datetime.now(), email))

                conn.commit()
                conn.close()
                return True
            except Exception as e:
                print(f"Error marking contact as contacted: {e}")
                return False

    def update_contact_phone(self, email: str, new_phone: str) -> bool:
        """Update phone number for existing contact."""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                # If phone changed to +86 and not contacted yet, reset message_sent
                if new_phone.startswith('+86'):
                    cursor.execute('''
                        UPDATE contacts
                        SET phone = ?, message_sent = 0
                        WHERE email = ? AND message_sent = 0
                    ''', (new_phone, email))
                else:
                    cursor.execute('''
                        UPDATE contacts
                        SET phone = ?
                        WHERE email = ?
                    ''', (new_phone, email))

                conn.commit()
                conn.close()
                return True
            except Exception as e:
                print(f"Error updating contact phone: {e}")
                return False

    def get_stats(self) -> Dict:
        """Get statistics about contacts."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('SELECT COUNT(*) FROM contacts')
            total = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM contacts WHERE message_sent = 1')
            contacted = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM contacts WHERE phone LIKE "+86%"')
            china_contacts = cursor.fetchone()[0]

            conn.close()

            return {
                'total_contacts': total,
                'contacted': contacted,
                'pending': total - contacted,
                'china_contacts': china_contacts
            }
