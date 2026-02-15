"""
Slack Connector - Complete Slack API Integration
Supports messages, channels, files, users, and workspace management
"""

import requests
import json
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

class SlackConnector:
    """
    Complete Slack API connector for workspace automation
    """
    
    def __init__(self, token: str, bot_token: Optional[str] = None):
        self.token = token
        self.bot_token = bot_token or token
        self.base_url = "https://slack.com/api"
        self.logger = logging.getLogger(__name__)
    
    def _make_request(
        self,
        endpoint: str,
        method: str = "POST",
        data: Optional[Dict] = None,
        use_bot_token: bool = True
    ) -> Dict[str, Any]:
        """Make API request to Slack"""
        token = self.bot_token if use_bot_token else self.token
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}/{endpoint}"
        
        if method == "POST":
            response = requests.post(url, headers=headers, json=data)
        else:
            response = requests.get(url, headers=headers, params=data)
        
        return response.json()
    
    # MESSAGES
    
    def send_message(
        self,
        channel: str,
        text: str,
        thread_ts: Optional[str] = None,
        blocks: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Send a message to a channel"""
        data = {
            "channel": channel,
            "text": text
        }
        
        if thread_ts:
            data["thread_ts"] = thread_ts
        
        if blocks:
            data["blocks"] = blocks
        
        result = self._make_request("chat.postMessage", data=data)
        
        if result.get("ok"):
            self.logger.info(f"Message sent to {channel}")
        else:
            self.logger.error(f"Failed to send message: {result.get('error')}")
        
        return result
    
    def update_message(
        self,
        channel: str,
        timestamp: str,
        text: str,
        blocks: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Update an existing message"""
        data = {
            "channel": channel,
            "ts": timestamp,
            "text": text
        }
        
        if blocks:
            data["blocks"] = blocks
        
        return self._make_request("chat.update", data=data)
    
    def delete_message(self, channel: str, timestamp: str) -> Dict[str, Any]:
        """Delete a message"""
        data = {
            "channel": channel,
            "ts": timestamp
        }
        
        return self._make_request("chat.delete", data=data)
    
    def get_message_history(
        self,
        channel: str,
        limit: int = 100,
        oldest: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get message history from a channel"""
        data = {
            "channel": channel,
            "limit": limit
        }
        
        if oldest:
            data["oldest"] = oldest
        
        result = self._make_request("conversations.history", method="GET", data=data)
        
        return result.get("messages", [])
    
    def add_reaction(self, channel: str, timestamp: str, emoji: str) -> Dict[str, Any]:
        """Add emoji reaction to a message"""
        data = {
            "channel": channel,
            "timestamp": timestamp,
            "name": emoji
        }
        
        return self._make_request("reactions.add", data=data)
    
    # CHANNELS
    
    def list_channels(self, types: str = "public_channel") -> List[Dict[str, Any]]:
        """
        List channels
        types: public_channel, private_channel, mpim, im
        """
        data = {
            "types": types,
            "exclude_archived": True
        }
        
        result = self._make_request("conversations.list", method="GET", data=data)
        
        return result.get("channels", [])
    
    def create_channel(
        self,
        name: str,
        is_private: bool = False
    ) -> Dict[str, Any]:
        """Create a new channel"""
        data = {
            "name": name,
            "is_private": is_private
        }
        
        result = self._make_request("conversations.create", data=data)
        
        if result.get("ok"):
            self.logger.info(f"Channel created: {name}")
        
        return result
    
    def archive_channel(self, channel: str) -> Dict[str, Any]:
        """Archive a channel"""
        data = {"channel": channel}
        return self._make_request("conversations.archive", data=data)
    
    def invite_to_channel(self, channel: str, users: List[str]) -> Dict[str, Any]:
        """Invite users to a channel"""
        data = {
            "channel": channel,
            "users": ",".join(users)
        }
        
        return self._make_request("conversations.invite", data=data)
    
    def get_channel_info(self, channel: str) -> Dict[str, Any]:
        """Get channel information"""
        data = {"channel": channel}
        
        result = self._make_request("conversations.info", method="GET", data=data)
        
        return result.get("channel", {})
    
    # USERS
    
    def list_users(self) -> List[Dict[str, Any]]:
        """List all users in workspace"""
        result = self._make_request("users.list", method="GET")
        
        return result.get("members", [])
    
    def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """Get user information"""
        data = {"user": user_id}
        
        result = self._make_request("users.info", method="GET", data=data)
        
        return result.get("user", {})
    
    def get_user_presence(self, user_id: str) -> str:
        """Get user presence status"""
        data = {"user": user_id}
        
        result = self._make_request("users.getPresence", method="GET", data=data)
        
        return result.get("presence", "unknown")
    
    def set_user_status(self, status_text: str, status_emoji: str) -> Dict[str, Any]:
        """Set user status"""
        data = {
            "profile": {
                "status_text": status_text,
                "status_emoji": status_emoji
            }
        }
        
        return self._make_request("users.profile.set", data=data)
    
    # FILES
    
    def upload_file(
        self,
        file_path: str,
        channels: Optional[List[str]] = None,
        title: Optional[str] = None,
        initial_comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """Upload a file to Slack"""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            
            data = {}
            if channels:
                data['channels'] = ','.join(channels)
            if title:
                data['title'] = title
            if initial_comment:
                data['initial_comment'] = initial_comment
            
            headers = {"Authorization": f"Bearer {self.bot_token}"}
            
            response = requests.post(
                f"{self.base_url}/files.upload",
                headers=headers,
                files=files,
                data=data
            )
        
        return response.json()
    
    def list_files(self, user: Optional[str] = None, channel: Optional[str] = None) -> List[Dict[str, Any]]:
        """List files"""
        data = {}
        if user:
            data['user'] = user
        if channel:
            data['channel'] = channel
        
        result = self._make_request("files.list", method="GET", data=data)
        
        return result.get("files", [])
    
    def delete_file(self, file_id: str) -> Dict[str, Any]:
        """Delete a file"""
        data = {"file": file_id}
        return self._make_request("files.delete", data=data)
    
    # WORKFLOWS & AUTOMATION
    
    def send_scheduled_message(
        self,
        channel: str,
        text: str,
        post_at: int
    ) -> Dict[str, Any]:
        """Schedule a message for later"""
        data = {
            "channel": channel,
            "text": text,
            "post_at": post_at
        }
        
        return self._make_request("chat.scheduleMessage", data=data)
    
    def list_scheduled_messages(self, channel: Optional[str] = None) -> List[Dict[str, Any]]:
        """List scheduled messages"""
        data = {}
        if channel:
            data['channel'] = channel
        
        result = self._make_request("chat.scheduledMessages.list", method="GET", data=data)
        
        return result.get("scheduled_messages", [])
    
    # SEARCH
    
    def search_messages(self, query: str, count: int = 20) -> List[Dict[str, Any]]:
        """Search for messages"""
        data = {
            "query": query,
            "count": count
        }
        
        result = self._make_request("search.messages", method="GET", data=data)
        
        return result.get("messages", {}).get("matches", [])
    
    # REMINDERS
    
    def create_reminder(
        self,
        text: str,
        time: str,
        user: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a reminder"""
        data = {
            "text": text,
            "time": time
        }
        
        if user:
            data['user'] = user
        
        return self._make_request("reminders.add", data=data)
    
    def list_reminders(self) -> List[Dict[str, Any]]:
        """List all reminders"""
        result = self._make_request("reminders.list", method="GET")
        
        return result.get("reminders", [])
    
    # WORKSPACE INFO
    
    def get_team_info(self) -> Dict[str, Any]:
        """Get workspace/team information"""
        result = self._make_request("team.info", method="GET")
        
        return result.get("team", {})
    
    def get_auth_test(self) -> Dict[str, Any]:
        """Test authentication and get bot info"""
        return self._make_request("auth.test", method="GET")
    
    # UTILITIES
    
    def send_formatted_message(
        self,
        channel: str,
        title: str,
        text: str,
        color: str = "good"
    ) -> Dict[str, Any]:
        """Send a formatted message with attachment"""
        attachments = [{
            "title": title,
            "text": text,
            "color": color
        }]
        
        data = {
            "channel": channel,
            "attachments": attachments
        }
        
        return self._make_request("chat.postMessage", data=data)
    
    def send_interactive_message(
        self,
        channel: str,
        text: str,
        buttons: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Send a message with interactive buttons
        
        buttons format: [{"text": "Click Me", "value": "button1"}]
        """
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": text
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": btn["text"]
                        },
                        "value": btn["value"]
                    }
                    for btn in buttons
                ]
            }
        ]
        
        return self.send_message(channel, text, blocks=blocks)


# Example usage
if __name__ == "__main__":
    # Initialize connector
    # slack = SlackConnector(token="xoxb-your-bot-token")
    
    # Send message
    # slack.send_message(
    #     channel="general",
    #     text="Hello from AI Agentic Framework!"
    # )
    
    # Create channel
    # slack.create_channel("ai-notifications")
    
    # Upload file
    # slack.upload_file(
    #     file_path="report.pdf",
    #     channels=["general"],
    #     title="Daily Report"
    # )
    
    print("Slack Connector ready!")
    print("Note: Requires Slack Bot Token")
