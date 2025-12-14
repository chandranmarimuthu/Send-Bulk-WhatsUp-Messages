"""
WhatsApp Bulk Message Sender
Automated tool to send WhatsApp messages to multiple contacts from CSV
Uses Selenium to keep browser session open and send messages one by one
"""

import pandas as pd
import time
from datetime import datetime
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WhatsAppBulkSender:
    """Send WhatsApp messages to bulk contacts using Selenium (single browser session)"""
    
    def __init__(self, csv_file: str, wait_time: int = 2):
        """
        Initialize the bulk sender
        
        Args:
            csv_file: Path to CSV file with contacts
            wait_time: Time to wait between messages (seconds)
        """
        self.csv_file = csv_file
        self.wait_time = wait_time
        self.contacts = []
        self.sent_messages = []
        self.failed_messages = []
        self.driver = None
    
    def load_contacts(self) -> bool:
        """Load contacts from CSV file"""
        try:
            df = pd.read_csv(self.csv_file, encoding='utf-8')
            
            # Validate required columns
            required_cols = ['phone_number', 'name']
            if not all(col in df.columns for col in required_cols):
                logger.error(f"CSV must contain columns: {required_cols}")
                return False
            
            self.contacts = df.to_dict('records')
            logger.info(f"Loaded {len(self.contacts)} contacts from {self.csv_file}")
            return True
        except FileNotFoundError:
            logger.error(f"CSV file not found: {self.csv_file}")
            return False
        except Exception as e:
            logger.error(f"Error loading CSV: {str(e)}")
            return False
    
    def format_phone_number(self, phone: str) -> str:
        """Format phone number to international format"""
        # Convert to string if it's an integer
        phone = str(phone).strip()
        
        # Remove common separators
        phone = phone.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
        
        # If doesn't start with +, assume India (+91)
        if not phone.startswith('+'):
            if not phone.startswith('91'):
                phone = f"+91{phone}"
            else:
                phone = f"+{phone}"
        
        return phone
    
    def open_whatsapp_web(self) -> bool:
        """Open WhatsApp Web in Chrome - call this once before sending"""
        try:
            logger.info("Opening WhatsApp Web... Please scan QR code when browser opens")
            
            # Chrome options
            chrome_options = Options()
            # Don't use headless mode - user needs to see and interact
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            # Initialize Chrome driver
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # Open WhatsApp Web
            self.driver.get("https://web.whatsapp.com")
            
            # Wait for user to scan QR code (30 seconds timeout)
            logger.info("Waiting for QR code scan... (timeout: 30 seconds)")
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='3']"))
            )
            
            logger.info("✓ WhatsApp Web loaded successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Failed to open WhatsApp Web: {str(e)}")
            if self.driver:
                self.driver.quit()
            self.driver = None
            return False
    
    def send_message(self, phone: str, message: str, name: str = "") -> bool:
        """
        Send a single WhatsApp message using existing browser session
        
        Args:
            phone: Phone number (with country code)
            message: Message text to send
            name: Contact name (for logging)
        
        Returns:
            True if successful, False otherwise
        """
        if not self.driver:
            logger.error("Browser not initialized. Call open_whatsapp_web() first.")
            return False
        
        try:
            formatted_phone = self.format_phone_number(phone)
            logger.info(f"Sending to {name} ({formatted_phone})...")
            
            # Open chat with contact
            # Use WhatsApp Web API URL format
            chat_url = f"https://web.whatsapp.com/send/?phone={formatted_phone}&text={message}"
            self.driver.get(chat_url)
            
            # Wait for message input field to appear
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//button[@aria-label='Send']"))
            )
            
            # Find and click Send button
            send_button = self.driver.find_element(By.XPATH, "//button[@aria-label='Send']")
            send_button.click()
            
            logger.info(f"✓ Message sent to {name} ({formatted_phone})")
            self.sent_messages.append({
                'name': name,
                'phone': formatted_phone,
                'timestamp': datetime.now(),
                'status': 'sent'
            })
            
            # Wait between messages
            time.sleep(self.wait_time)
            return True
        
        except Exception as e:
            error_msg = str(e)
            log_msg = f"✗ Failed to send to {name} ({phone}): {error_msg}"
            logger.error(log_msg)
            self.failed_messages.append({
                'name': name,
                'phone': phone,
                'timestamp': datetime.now(),
                'error': error_msg
            })
            return False
    
    def send_bulk_messages(self, message: str, delay_seconds: int = 5) -> dict:
        """
        Send messages to all loaded contacts using single browser session
        
        Args:
            message: Message template (use {name} for personalization)
            delay_seconds: Delay between messages
        
        Returns:
            Dict with summary statistics
        """
        if not self.contacts:
            logger.error("No contacts loaded. Call load_contacts() first.")
            return None
        
        # Open WhatsApp Web once
        if not self.open_whatsapp_web():
            return None
        
        logger.info(f"Starting bulk send to {len(self.contacts)} contacts")
        
        try:
            for i, contact in enumerate(self.contacts, 1):
                phone = contact.get('phone_number', '')
                name = contact.get('name', 'Unknown')
                
                # Personalize message
                personalized_msg = message.format(**contact)
                
                logger.info(f"[{i}/{len(self.contacts)}] Sending to {name}...")
                
                self.send_message(phone, personalized_msg, name)
                
                # Delay between messages
                if i < len(self.contacts):
                    time.sleep(delay_seconds)
        
        finally:
            # Close browser
            if self.driver:
                self.driver.quit()
                self.driver = None
        
        # Return summary
        return {
            'total': len(self.contacts),
            'sent': len(self.sent_messages),
            'failed': len(self.failed_messages),
            'success_rate': (len(self.sent_messages) / len(self.contacts) * 100) if self.contacts else 0
        }
    
    def get_report(self) -> dict:
        """Get detailed report of sent/failed messages"""
        return {
            'sent': self.sent_messages,
            'failed': self.failed_messages,
            'summary': {
                'total_sent': len(self.sent_messages),
                'total_failed': len(self.failed_messages),
                'success_rate': (len(self.sent_messages) / (len(self.sent_messages) + len(self.failed_messages)) * 100) 
                                if (self.sent_messages or self.failed_messages) else 0
            }
        }
    
    def close_browser(self):
        """Close browser if open"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.info("Browser closed")
