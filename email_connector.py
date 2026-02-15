"""
Email Connector - SMTP and IMAP Email Integration
Supports Gmail, Outlook, and custom SMTP/IMAP servers
"""

import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, List, Optional, Any, Tuple
import logging
from datetime import datetime
import os

class EmailConnector:
    """
    Complete email connector supporting SMTP and IMAP
    """
    
    # Common email providers
    PROVIDERS = {
        "gmail": {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "imap_server": "imap.gmail.com",
            "imap_port": 993
        },
        "outlook": {
            "smtp_server": "smtp-mail.outlook.com",
            "smtp_port": 587,
            "imap_server": "outlook.office365.com",
            "imap_port": 993
        },
        "yahoo": {
            "smtp_server": "smtp.mail.yahoo.com",
            "smtp_port": 587,
            "imap_server": "imap.mail.yahoo.com",
            "imap_port": 993
        }
    }
    
    def __init__(
        self,
        email_address: str,
        password: str,
        provider: str = "gmail",
        smtp_server: Optional[str] = None,
        smtp_port: Optional[int] = None,
        imap_server: Optional[str] = None,
        imap_port: Optional[int] = None
    ):
        self.email_address = email_address
        self.password = password
        self.logger = logging.getLogger(__name__)
        
        # Set server configurations
        if provider in self.PROVIDERS:
            config = self.PROVIDERS[provider]
            self.smtp_server = smtp_server or config["smtp_server"]
            self.smtp_port = smtp_port or config["smtp_port"]
            self.imap_server = imap_server or config["imap_server"]
            self.imap_port = imap_port or config["imap_port"]
        else:
            self.smtp_server = smtp_server
            self.smtp_port = smtp_port or 587
            self.imap_server = imap_server
            self.imap_port = imap_port or 993
        
        self.smtp_connection = None
        self.imap_connection = None
    
    # SENDING EMAILS (SMTP)
    
    def connect_smtp(self) -> bool:
        """Connect to SMTP server"""
        try:
            self.smtp_connection = smtplib.SMTP(self.smtp_server, self.smtp_port)
            self.smtp_connection.starttls()
            self.smtp_connection.login(self.email_address, self.password)
            self.logger.info("SMTP connected successfully")
            return True
        except Exception as e:
            self.logger.error(f"SMTP connection failed: {e}")
            return False
    
    def disconnect_smtp(self):
        """Disconnect from SMTP server"""
        if self.smtp_connection:
            self.smtp_connection.quit()
            self.smtp_connection = None
    
    def send_email(
        self,
        to: List[str],
        subject: str,
        body: str,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[str]] = None,
        html: bool = False
    ) -> bool:
        """Send an email"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = ', '.join(to)
            msg['Subject'] = subject
            
            if cc:
                msg['Cc'] = ', '.join(cc)
            
            # Add body
            mime_type = 'html' if html else 'plain'
            msg.attach(MIMEText(body, mime_type))
            
            # Add attachments
            if attachments:
                for file_path in attachments:
                    self._attach_file(msg, file_path)
            
            # Connect and send
            if not self.smtp_connection:
                self.connect_smtp()
            
            recipients = to + (cc or []) + (bcc or [])
            
            self.smtp_connection.send_message(msg)
            
            self.logger.info(f"Email sent to {', '.join(to)}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return False
    
    def _attach_file(self, msg: MIMEMultipart, file_path: str):
        """Attach a file to email"""
        try:
            with open(file_path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
            
            encoders.encode_base64(part)
            
            filename = os.path.basename(file_path)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {filename}'
            )
            
            msg.attach(part)
            
        except Exception as e:
            self.logger.error(f"Failed to attach file {file_path}: {e}")
    
    def send_html_email(
        self,
        to: List[str],
        subject: str,
        html_content: str,
        attachments: Optional[List[str]] = None
    ) -> bool:
        """Send an HTML email"""
        return self.send_email(to, subject, html_content, attachments=attachments, html=True)
    
    # READING EMAILS (IMAP)
    
    def connect_imap(self) -> bool:
        """Connect to IMAP server"""
        try:
            self.imap_connection = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            self.imap_connection.login(self.email_address, self.password)
            self.logger.info("IMAP connected successfully")
            return True
        except Exception as e:
            self.logger.error(f"IMAP connection failed: {e}")
            return False
    
    def disconnect_imap(self):
        """Disconnect from IMAP server"""
        if self.imap_connection:
            self.imap_connection.close()
            self.imap_connection.logout()
            self.imap_connection = None
    
    def list_folders(self) -> List[str]:
        """List all email folders"""
        if not self.imap_connection:
            self.connect_imap()
        
        status, folders = self.imap_connection.list()
        
        folder_names = []
        for folder in folders:
            folder_name = folder.decode().split(' "/" ')[-1]
            folder_names.append(folder_name)
        
        return folder_names
    
    def get_emails(
        self,
        folder: str = "INBOX",
        limit: int = 10,
        unread_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Get emails from a folder"""
        if not self.imap_connection:
            self.connect_imap()
        
        self.imap_connection.select(folder)
        
        # Search criteria
        search_criteria = "UNSEEN" if unread_only else "ALL"
        
        status, messages = self.imap_connection.search(None, search_criteria)
        
        email_ids = messages[0].split()
        email_ids = email_ids[-limit:]  # Get last N emails
        
        emails = []
        
        for email_id in email_ids:
            email_data = self._fetch_email(email_id)
            if email_data:
                emails.append(email_data)
        
        return emails
    
    def _fetch_email(self, email_id: bytes) -> Optional[Dict[str, Any]]:
        """Fetch a single email"""
        try:
            status, msg_data = self.imap_connection.fetch(email_id, '(RFC822)')
            
            email_body = msg_data[0][1]
            email_message = email.message_from_bytes(email_body)
            
            # Extract email data
            subject = email_message['subject']
            from_addr = email_message['from']
            to_addr = email_message['to']
            date = email_message['date']
            
            # Extract body
            body = ""
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode()
                        break
            else:
                body = email_message.get_payload(decode=True).decode()
            
            return {
                "id": email_id.decode(),
                "subject": subject,
                "from": from_addr,
                "to": to_addr,
                "date": date,
                "body": body
            }
            
        except Exception as e:
            self.logger.error(f"Failed to fetch email: {e}")
            return None
    
    def search_emails(
        self,
        folder: str = "INBOX",
        subject: Optional[str] = None,
        from_addr: Optional[str] = None,
        since_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search emails with criteria"""
        if not self.imap_connection:
            self.connect_imap()
        
        self.imap_connection.select(folder)
        
        # Build search criteria
        criteria = []
        
        if subject:
            criteria.append(f'SUBJECT "{subject}"')
        
        if from_addr:
            criteria.append(f'FROM "{from_addr}"')
        
        if since_date:
            criteria.append(f'SINCE "{since_date}"')
        
        search_string = ' '.join(criteria) if criteria else 'ALL'
        
        status, messages = self.imap_connection.search(None, search_string)
        
        email_ids = messages[0].split()
        
        emails = []
        for email_id in email_ids:
            email_data = self._fetch_email(email_id)
            if email_data:
                emails.append(email_data)
        
        return emails
    
    def mark_as_read(self, email_id: str, folder: str = "INBOX"):
        """Mark email as read"""
        if not self.imap_connection:
            self.connect_imap()
        
        self.imap_connection.select(folder)
        self.imap_connection.store(email_id, '+FLAGS', '\\Seen')
    
    def mark_as_unread(self, email_id: str, folder: str = "INBOX"):
        """Mark email as unread"""
        if not self.imap_connection:
            self.connect_imap()
        
        self.imap_connection.select(folder)
        self.imap_connection.store(email_id, '-FLAGS', '\\Seen')
    
    def delete_email(self, email_id: str, folder: str = "INBOX"):
        """Delete an email"""
        if not self.imap_connection:
            self.connect_imap()
        
        self.imap_connection.select(folder)
        self.imap_connection.store(email_id, '+FLAGS', '\\Deleted')
        self.imap_connection.expunge()
    
    def get_unread_count(self, folder: str = "INBOX") -> int:
        """Get count of unread emails"""
        if not self.imap_connection:
            self.connect_imap()
        
        self.imap_connection.select(folder)
        status, messages = self.imap_connection.search(None, 'UNSEEN')
        
        return len(messages[0].split())
    
    # UTILITIES
    
    def __enter__(self):
        """Context manager entry"""
        self.connect_smtp()
        self.connect_imap()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect_smtp()
        self.disconnect_imap()


# Example usage
if __name__ == "__main__":
    # Initialize connector
    # email = EmailConnector(
    #     email_address="your@gmail.com",
    #     password="your_app_password",
    #     provider="gmail"
    # )
    
    # Send email
    # email.send_email(
    #     to=["recipient@example.com"],
    #     subject="Test Email",
    #     body="This is a test from AI Agentic Framework"
    # )
    
    # Get unread emails
    # emails = email.get_emails(unread_only=True, limit=5)
    
    print("Email Connector ready!")
    print("Note: For Gmail, use App Password (not regular password)")
