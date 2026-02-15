"""
Connector Manager - Unified interface for all connectors
Manages GitHub, Google Drive, Slack, Email, and more
"""

import logging
from typing import Dict, List, Optional, Any
import json

# Import all connectors
try:
    from github_connector import GitHubConnector
    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False

try:
    from google_drive_connector import GoogleDriveConnector
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False

try:
    from slack_connector import SlackConnector
    SLACK_AVAILABLE = True
except ImportError:
    SLACK_AVAILABLE = False

try:
    from email_connector import EmailConnector
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False

class ConnectorManager:
    """
    Unified manager for all connectors
    Provides single interface to interact with multiple services
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        self.connectors: Dict[str, Any] = {}
        
        self.logger.info("Connector Manager initialized")
    
    # INITIALIZATION
    
    def add_github(self, token: str, username: Optional[str] = None) -> bool:
        """Add GitHub connector"""
        if not GITHUB_AVAILABLE:
            self.logger.error("GitHub connector not available")
            return False
        
        try:
            self.connectors['github'] = GitHubConnector(token, username)
            self.logger.info("GitHub connector added")
            return True
        except Exception as e:
            self.logger.error(f"Failed to add GitHub connector: {e}")
            return False
    
    def add_google_drive(
        self,
        credentials_path: str = 'credentials.json',
        token_path: str = 'token.json'
    ) -> bool:
        """Add Google Drive connector"""
        if not GOOGLE_DRIVE_AVAILABLE:
            self.logger.error("Google Drive connector not available")
            return False
        
        try:
            self.connectors['google_drive'] = GoogleDriveConnector(
                credentials_path, token_path
            )
            self.logger.info("Google Drive connector added")
            return True
        except Exception as e:
            self.logger.error(f"Failed to add Google Drive connector: {e}")
            return False
    
    def add_slack(self, token: str, bot_token: Optional[str] = None) -> bool:
        """Add Slack connector"""
        if not SLACK_AVAILABLE:
            self.logger.error("Slack connector not available")
            return False
        
        try:
            self.connectors['slack'] = SlackConnector(token, bot_token)
            self.logger.info("Slack connector added")
            return True
        except Exception as e:
            self.logger.error(f"Failed to add Slack connector: {e}")
            return False
    
    def add_email(
        self,
        email_address: str,
        password: str,
        provider: str = "gmail"
    ) -> bool:
        """Add Email connector"""
        if not EMAIL_AVAILABLE:
            self.logger.error("Email connector not available")
            return False
        
        try:
            self.connectors['email'] = EmailConnector(
                email_address, password, provider
            )
            self.logger.info("Email connector added")
            return True
        except Exception as e:
            self.logger.error(f"Failed to add Email connector: {e}")
            return False
    
    # UNIFIED OPERATIONS
    
    def send_notification(
        self,
        service: str,
        message: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send notification to any service
        
        service: 'slack', 'email'
        """
        if service == 'slack' and 'slack' in self.connectors:
            channel = kwargs.get('channel', 'general')
            return self.connectors['slack'].send_message(channel, message)
        
        elif service == 'email' and 'email' in self.connectors:
            to = kwargs.get('to', [])
            subject = kwargs.get('subject', 'Notification')
            return {
                "success": self.connectors['email'].send_email(to, subject, message)
            }
        
        else:
            return {"error": f"Service {service} not available"}
    
    def upload_file(
        self,
        service: str,
        file_path: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Upload file to any service
        
        service: 'github', 'google_drive', 'slack'
        """
        if service == 'github' and 'github' in self.connectors:
            owner = kwargs.get('owner')
            repo = kwargs.get('repo')
            path = kwargs.get('path')
            
            with open(file_path, 'r') as f:
                content = f.read()
            
            return self.connectors['github'].create_file(
                owner, repo, path, content
            )
        
        elif service == 'google_drive' and 'google_drive' in self.connectors:
            folder_id = kwargs.get('folder_id')
            return self.connectors['google_drive'].upload_file(file_path, folder_id)
        
        elif service == 'slack' and 'slack' in self.connectors:
            channels = kwargs.get('channels', [])
            return self.connectors['slack'].upload_file(file_path, channels)
        
        else:
            return {"error": f"Service {service} not available"}
    
    def search(
        self,
        service: str,
        query: str,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Search across services
        
        service: 'github', 'google_drive', 'slack', 'email'
        """
        if service == 'github' and 'github' in self.connectors:
            return self.connectors['github'].search_repositories(query)
        
        elif service == 'google_drive' and 'google_drive' in self.connectors:
            return self.connectors['google_drive'].search_files(query)
        
        elif service == 'slack' and 'slack' in self.connectors:
            return self.connectors['slack'].search_messages(query)
        
        elif service == 'email' and 'email' in self.connectors:
            return self.connectors['email'].search_emails(subject=query)
        
        else:
            return []
    
    # GITHUB SPECIFIC
    
    def create_github_repo(
        self,
        name: str,
        description: str = "",
        private: bool = False
    ) -> Dict[str, Any]:
        """Create GitHub repository"""
        if 'github' not in self.connectors:
            return {"error": "GitHub connector not configured"}
        
        return self.connectors['github'].create_repository(name, description, private)
    
    def push_to_github(
        self,
        owner: str,
        repo: str,
        files: List[Dict[str, str]],
        message: str = "Update files"
    ) -> Dict[str, Any]:
        """Push multiple files to GitHub"""
        if 'github' not in self.connectors:
            return {"error": "GitHub connector not configured"}
        
        return self.connectors['github'].commit_multiple_files(
            owner, repo, files, message
        )
    
    # GOOGLE DRIVE SPECIFIC
    
    def create_drive_folder(self, folder_name: str) -> Dict[str, Any]:
        """Create Google Drive folder"""
        if 'google_drive' not in self.connectors:
            return {"error": "Google Drive connector not configured"}
        
        return self.connectors['google_drive'].create_folder(folder_name)
    
    def download_from_drive(self, file_id: str, destination: str) -> bool:
        """Download file from Google Drive"""
        if 'google_drive' not in self.connectors:
            return False
        
        return self.connectors['google_drive'].download_file(file_id, destination)
    
    # SLACK SPECIFIC
    
    def send_slack_message(
        self,
        channel: str,
        text: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Send Slack message"""
        if 'slack' not in self.connectors:
            return {"error": "Slack connector not configured"}
        
        return self.connectors['slack'].send_message(channel, text, **kwargs)
    
    def create_slack_channel(self, name: str, is_private: bool = False) -> Dict[str, Any]:
        """Create Slack channel"""
        if 'slack' not in self.connectors:
            return {"error": "Slack connector not configured"}
        
        return self.connectors['slack'].create_channel(name, is_private)
    
    # EMAIL SPECIFIC
    
    def send_email(
        self,
        to: List[str],
        subject: str,
        body: str,
        **kwargs
    ) -> bool:
        """Send email"""
        if 'email' not in self.connectors:
            return False
        
        return self.connectors['email'].send_email(to, subject, body, **kwargs)
    
    def get_unread_emails(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get unread emails"""
        if 'email' not in self.connectors:
            return []
        
        return self.connectors['email'].get_emails(unread_only=True, limit=limit)
    
    # UTILITIES
    
    def list_connectors(self) -> List[str]:
        """List all active connectors"""
        return list(self.connectors.keys())
    
    def get_connector(self, name: str) -> Optional[Any]:
        """Get specific connector"""
        return self.connectors.get(name)
    
    def remove_connector(self, name: str) -> bool:
        """Remove a connector"""
        if name in self.connectors:
            del self.connectors[name]
            self.logger.info(f"Removed connector: {name}")
            return True
        return False
    
    def test_all_connectors(self) -> Dict[str, bool]:
        """Test all connectors"""
        results = {}
        
        if 'github' in self.connectors:
            try:
                self.connectors['github'].get_user_info()
                results['github'] = True
            except:
                results['github'] = False
        
        if 'slack' in self.connectors:
            try:
                self.connectors['slack'].get_auth_test()
                results['slack'] = True
            except:
                results['slack'] = False
        
        if 'google_drive' in self.connectors:
            try:
                self.connectors['google_drive'].get_storage_quota()
                results['google_drive'] = True
            except:
                results['google_drive'] = False
        
        if 'email' in self.connectors:
            try:
                self.connectors['email'].get_unread_count()
                results['email'] = True
            except:
                results['email'] = False
        
        return results
    
    def export_config(self, filepath: str):
        """Export connector configuration (without sensitive data)"""
        config = {
            "connectors": list(self.connectors.keys()),
            "timestamp": datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(config, f, indent=2)
        
        self.logger.info(f"Configuration exported to {filepath}")


# Example usage
if __name__ == "__main__":
    from datetime import datetime
    
    # Initialize manager
    manager = ConnectorManager()
    
    # Add connectors
    # manager.add_github(token="your_token")
    # manager.add_slack(token="your_slack_token")
    # manager.add_email("your@email.com", "password")
    
    # Use unified interface
    # manager.send_notification('slack', 'Hello from framework!', channel='general')
    # manager.upload_file('github', 'file.py', owner='user', repo='repo', path='file.py')
    
    print("Connector Manager ready!")
    print(f"Available connectors: {manager.list_connectors()}")
