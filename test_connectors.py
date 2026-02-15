"""
Quick Connector Test - Test all your connectors
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_github():
    """Test GitHub connector"""
    print("\n🔍 Testing GitHub Connector...")
    try:
        from github_connector import GitHubConnector
        
        token = os.getenv('GITHUB_TOKEN')
        if not token:
            print("❌ GITHUB_TOKEN not found in environment")
            return False
        
        github = GitHubConnector(token=token)
        user_info = github.get_user_info()
        
        print(f"✅ GitHub connected! User: {user_info.get('login', 'Unknown')}")
        return True
    except Exception as e:
        print(f"❌ GitHub failed: {e}")
        return False

def test_slack():
    """Test Slack connector"""
    print("\n🔍 Testing Slack Connector...")
    try:
        from slack_connector import SlackConnector
        
        token = os.getenv('SLACK_TOKEN')
        if not token:
            print("❌ SLACK_TOKEN not found in environment")
            return False
        
        slack = SlackConnector(token=token)
        auth = slack.get_auth_test()
        
        if auth.get('ok'):
            print(f"✅ Slack connected! Team: {auth.get('team', 'Unknown')}")
            return True
        else:
            print(f"❌ Slack authentication failed")
            return False
    except Exception as e:
        print(f"❌ Slack failed: {e}")
        return False

def test_email():
    """Test Email connector"""
    print("\n🔍 Testing Email Connector...")
    try:
        from email_connector import EmailConnector
        
        email_addr = os.getenv('GMAIL_EMAIL')
        password = os.getenv('GMAIL_PASSWORD')
        
        if not email_addr or not password:
            print("❌ GMAIL_EMAIL or GMAIL_PASSWORD not found in environment")
            return False
        
        email = EmailConnector(email_addr, password, provider='gmail')
        email.connect_imap()
        
        unread_count = email.get_unread_count()
        email.disconnect_imap()
        
        print(f"✅ Email connected! Unread emails: {unread_count}")
        return True
    except Exception as e:
        print(f"❌ Email failed: {e}")
        return False

def test_google_drive():
    """Test Google Drive connector"""
    print("\n🔍 Testing Google Drive Connector...")
    try:
        from google_drive_connector import GoogleDriveConnector
        
        creds_path = os.getenv('GOOGLE_CREDENTIALS', 'credentials.json')
        
        if not os.path.exists(creds_path):
            print(f"❌ {creds_path} not found")
            return False
        
        drive = GoogleDriveConnector(credentials_path=creds_path)
        quota = drive.get_storage_quota()
        
        print(f"✅ Google Drive connected! User: {quota.get('user', 'Unknown')}")
        return True
    except Exception as e:
        print(f"❌ Google Drive failed: {e}")
        return False

def main():
    """Run all connector tests"""
    print("="*60)
    print("🧪 AI AGENTIC FRAMEWORK - CONNECTOR TEST")
    print("="*60)
    
    results = {
        "GitHub": test_github(),
        "Slack": test_slack(),
        "Email": test_email(),
        "Google Drive": test_google_drive()
    }
    
    print("\n" + "="*60)
    print("📊 TEST RESULTS")
    print("="*60)
    
    for service, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {service}: {'PASS' if status else 'FAIL'}")
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"\nTotal: {passed}/{total} connectors working")
    
    if passed == 0:
        print("\n💡 Setup Instructions:")
        print("1. Create .env file with your credentials")
        print("2. Add these variables:")
        print("   GITHUB_TOKEN=your_token")
        print("   SLACK_TOKEN=your_token")
        print("   GMAIL_EMAIL=your@gmail.com")
        print("   GMAIL_PASSWORD=your_app_password")
        print("   GOOGLE_CREDENTIALS=credentials.json")
        print("\n3. Install python-dotenv: pip install python-dotenv")
        print("4. See CONNECTORS.md for detailed setup")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
