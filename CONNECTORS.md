# 🔌 Connectors Guide

Complete guide to using all available connectors in the AI Agentic Framework.

## 📦 Available Connectors

1. **GitHub Connector** - Repository management, commits, pull requests
2. **Google Drive Connector** - File upload, download, search, sharing
3. **Slack Connector** - Messages, channels, files, automation
4. **Email Connector** - Send/receive emails via SMTP/IMAP
5. **Connector Manager** - Unified interface for all connectors

## 🚀 Quick Start

### Install Dependencies

```bash
# Install all connector dependencies
pip install -r requirements.txt

# Or install specific connectors:
pip install PyGithub  # GitHub only
pip install google-api-python-client google-auth  # Google Drive only
pip install slack-sdk  # Slack only
# Email uses Python built-in libraries
```

## 🔧 Connector Setup

### 1. GitHub Connector

**Get Token:**
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo`, `user`
4. Copy the token

**Usage:**
```python
from github_connector import GitHubConnector

# Initialize
github = GitHubConnector(
    token="ghp_your_token_here",
    username="your_username"
)

# Create repository
repo = github.create_repository(
    name="My-New-Repo",
    description="Created with AI Agentic Framework",
    private=False
)

# Upload file
github.create_file(
    owner="your_username",
    repo="My-New-Repo",
    path="README.md",
    content="# Hello World",
    message="Initial commit"
)

# Create issue
github.create_issue(
    owner="your_username",
    repo="My-New-Repo",
    title="Add documentation",
    body="Need to add docs"
)
```

### 2. Google Drive Connector

**Get Credentials:**
1. Go to https://console.cloud.google.com/
2. Create a new project
3. Enable Google Drive API
4. Create OAuth 2.0 credentials
5. Download as `credentials.json`

**Usage:**
```python
from google_drive_connector import GoogleDriveConnector

# Initialize (will open browser for auth first time)
drive = GoogleDriveConnector(
    credentials_path='credentials.json',
    token_path='token.json'
)

# Upload file
file = drive.upload_file('document.pdf')
print(f"Uploaded: {file['webViewLink']}")

# Create folder
folder = drive.create_folder('My Projects')

# Search files
files = drive.search_files('budget')

# Share file
drive.share_file(file['id'], email='friend@email.com', role='reader')
```

### 3. Slack Connector

**Get Token:**
1. Go to https://api.slack.com/apps
2. Create new app
3. Add Bot Token Scopes: `chat:write`, `channels:read`, `files:write`
4. Install app to workspace
5. Copy Bot User OAuth Token

**Usage:**
```python
from slack_connector import SlackConnector

# Initialize
slack = SlackConnector(token="xoxb-your-bot-token")

# Send message
slack.send_message(
    channel="general",
    text="Hello from AI Agentic Framework!"
)

# Create channel
slack.create_channel("ai-notifications")

# Upload file
slack.upload_file(
    file_path="report.pdf",
    channels=["general"],
    title="Daily Report"
)

# Get messages
messages = slack.get_message_history("general", limit=10)
```

### 4. Email Connector

**For Gmail:**
1. Enable 2-factor authentication
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use app password (not regular password)

**Usage:**
```python
from email_connector import EmailConnector

# Initialize
email = EmailConnector(
    email_address="your@gmail.com",
    password="your_app_password",
    provider="gmail"
)

# Send email
email.send_email(
    to=["recipient@example.com"],
    subject="Test Email",
    body="Hello from AI Framework",
    attachments=["report.pdf"]
)

# Get unread emails
unread = email.get_emails(unread_only=True, limit=5)

# Search emails
results = email.search_emails(subject="invoice", since_date="01-Jan-2024")
```

## 🎯 Unified Interface - Connector Manager

The Connector Manager provides a single interface for all connectors:

```python
from connector_manager import ConnectorManager

# Initialize
manager = ConnectorManager()

# Add connectors
manager.add_github(token="your_github_token")
manager.add_slack(token="your_slack_token")
manager.add_email("your@gmail.com", "app_password")

# Unified operations

# Send notification to any service
manager.send_notification('slack', 'Build complete!', channel='devops')
manager.send_notification('email', 'Build complete!', 
                         to=['team@company.com'], 
                         subject='CI/CD Alert')

# Upload file to any service
manager.upload_file('github', 'config.yaml', 
                   owner='user', repo='project', path='config.yaml')
manager.upload_file('google_drive', 'backup.zip', folder_id='folder123')

# Search across services
github_repos = manager.search('github', 'machine learning')
drive_files = manager.search('google_drive', 'budget 2024')
slack_msgs = manager.search('slack', 'deployment')

# Test all connectors
status = manager.test_all_connectors()
print(status)  # {'github': True, 'slack': True, 'email': True}
```

## 📚 Integration with AI Framework

### Use Connectors with Agents

```python
from ai_agentic_framework import AIAgenticFramework
from connector_manager import ConnectorManager
from agent_manager import AgentCapability

async def main():
    # Initialize framework
    framework = AIAgenticFramework()
    
    # Setup connectors
    connectors = ConnectorManager()
    connectors.add_github(token="token")
    connectors.add_slack(token="token")
    
    # Create agent
    await framework.initialize_agents([{
        "id": "automation_agent",
        "type": "research",
        "capabilities": [AgentCapability.RESEARCH]
    }])
    
    # Agent does research
    task_id = await framework.submit_task(
        "Research latest AI trends",
        priority=8
    )
    
    await framework.process_tasks()
    
    # Get results
    result = framework.agent_manager.completed_tasks[task_id]
    
    # Share results via connectors
    if result["status"] == "success":
        # Post to Slack
        connectors.send_slack_message(
            channel="research",
            text=f"Research complete: {result['result']['summary']}"
        )
        
        # Create GitHub issue
        github = connectors.get_connector('github')
        github.create_issue(
            owner="user",
            repo="research-repo",
            title="Latest AI Trends",
            body=result['result']['summary']
        )

asyncio.run(main())
```

## 🔐 Security Best Practices

### 1. Store Credentials Securely

**DON'T:**
```python
github = GitHubConnector(token="ghp_hardcoded_token_123")  # ❌ Bad!
```

**DO:**
```python
import os
github = GitHubConnector(token=os.environ.get('GITHUB_TOKEN'))  # ✅ Good!
```

**Setup environment variables:**
```bash
# Windows
setx GITHUB_TOKEN "your_token"
setx SLACK_TOKEN "your_token"

# Linux/Mac
export GITHUB_TOKEN="your_token"
export SLACK_TOKEN="your_token"
```

### 2. Use .env Files

Create `.env` file:
```
GITHUB_TOKEN=ghp_your_token
SLACK_TOKEN=xoxb_your_token
GMAIL_EMAIL=your@gmail.com
GMAIL_PASSWORD=your_app_password
```

Load in code:
```python
from dotenv import load_dotenv
import os

load_dotenv()

github = GitHubConnector(token=os.getenv('GITHUB_TOKEN'))
```

Install python-dotenv:
```bash
pip install python-dotenv
```

### 3. Never Commit Credentials

Add to `.gitignore`:
```
.env
credentials.json
token.json
*.pem
*.key
```

## 🎨 Advanced Examples

### Example 1: Automated Deployment

```python
from connector_manager import ConnectorManager

manager = ConnectorManager()
manager.add_github(token=os.getenv('GITHUB_TOKEN'))
manager.add_slack(token=os.getenv('SLACK_TOKEN'))

# Create release
github = manager.get_connector('github')
release = github.create_release(
    owner="user",
    repo="app",
    tag="v1.0.0",
    name="Version 1.0.0"
)

# Notify team
manager.send_slack_message(
    channel="releases",
    text=f"🚀 New release: {release['name']}",
    blocks=[{
        "type": "section",
        "text": {"type": "mrkdwn", "text": f"*{release['name']}*\n{release['url']}"}
    }]
)
```

### Example 2: Backup System

```python
import os
from connector_manager import ConnectorManager

manager = ConnectorManager()
manager.add_google_drive(credentials_path='creds.json')

# Backup folder
result = manager.get_connector('google_drive').upload_folder(
    folder_path='./important_data',
    parent_id='backup_folder_id'
)

print(f"Backed up {result['uploaded_count']} files")
```

### Example 3: Daily Report

```python
from connector_manager import ConnectorManager
from datetime import datetime

manager = ConnectorManager()
manager.add_email("reports@company.com", "password")

# Generate report
report = f"""
Daily Report - {datetime.now().strftime('%Y-%m-%d')}

Tasks Completed: 15
Bugs Fixed: 3
New Features: 2
"""

# Send to team
manager.send_email(
    to=["team@company.com"],
    subject=f"Daily Report {datetime.now().strftime('%Y-%m-%d')}",
    body=report
)
```

## 🐛 Troubleshooting

### GitHub

**Issue:** "Bad credentials"
- **Solution:** Regenerate token, ensure correct scopes

**Issue:** "Not Found"
- **Solution:** Check repository name and owner

### Google Drive

**Issue:** "Access denied"
- **Solution:** Re-authenticate, check API is enabled

**Issue:** "Quota exceeded"
- **Solution:** Check storage quota with `get_storage_quota()`

### Slack

**Issue:** "Token revoked"
- **Solution:** Reinstall app to workspace

**Issue:** "Channel not found"
- **Solution:** Use channel ID instead of name

### Email

**Issue:** "Authentication failed" (Gmail)
- **Solution:** Use App Password, not regular password

**Issue:** "Connection refused"
- **Solution:** Check SMTP/IMAP settings

## 📖 API Reference

See individual connector files for complete API documentation:
- `github_connector.py` - GitHub methods
- `google_drive_connector.py` - Google Drive methods
- `slack_connector.py` - Slack methods
- `email_connector.py` - Email methods
- `connector_manager.py` - Unified interface

## 🤝 Contributing

Want to add a new connector? Follow this template:

```python
class MyServiceConnector:
    def __init__(self, credentials):
        self.credentials = credentials
        self.logger = logging.getLogger(__name__)
    
    def connect(self):
        # Connection logic
        pass
    
    def send_data(self, data):
        # Send data
        pass
    
    def get_data(self, query):
        # Get data
        pass
```

Then add to `connector_manager.py`!

---

**Need help? Check the example code in each connector file!**
