"""
GitHub Connector Module
Automates GitHub operations: create repos, push code, manage issues, etc.
"""

import requests
import json
import os
from typing import Dict, List, Optional, Any
import logging

class GitHubConnector:
    """
    GitHub API Connector for automation
    
    Usage:
        # Set environment variable first
        set GITHUB_TOKEN=your_token_here
        
        # Then use the connector
        github = GitHubConnector()
        result = github.create_repository("AI-Agentic-Framework")
    """
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize GitHub connector
        
        Args:
            token: GitHub Personal Access Token
                   Or set GITHUB_TOKEN environment variable
                   Create at: https://github.com/settings/tokens/new
        """
        self.logger = logging.getLogger(__name__)
        self.token = token or os.getenv('GITHUB_TOKEN')
        
        if not self.token:
            raise ValueError(
                "GitHub token required!\n\n"
                "Steps:\n"
                "1. Go to: https://github.com/settings/tokens/new\n"
                "2. Create token with 'repo' scope\n"
                "3. Set environment variable:\n"
                "   Windows CMD: set GITHUB_TOKEN=your_token_here\n"
                "   PowerShell: $env:GITHUB_TOKEN='your_token_here'\n"
                "4. Run again"
            )
        
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Verify token
        self._verify_token()
    
    def _verify_token(self):
        """Verify GitHub token is valid"""
        response = requests.get(f"{self.base_url}/user", headers=self.headers)
        
        if response.status_code == 200:
            self.username = response.json()['login']
            self.logger.info(f"✓ Authenticated as: {self.username}")
        else:
            raise ValueError(f"Invalid GitHub token: {response.status_code}")
    
    def create_repository(
        self,
        name: str,
        description: str = "",
        private: bool = False
    ) -> Dict[str, Any]:
        """
        Create a new GitHub repository
        
        Args:
            name: Repository name (e.g., "AI-Agentic-Framework")
            description: Repository description
            private: Make repository private (default: False)
            
        Returns:
            {"success": True, "repo_url": "...", "clone_url": "..."}
        """
        print(f"\nCreating repository: {name}")
        
        data = {
            "name": name,
            "description": description,
            "private": private,
            "auto_init": True  # Create with README
        }
        
        response = requests.post(
            f"{self.base_url}/user/repos",
            headers=self.headers,
            json=data
        )
        
        if response.status_code == 201:
            repo_data = response.json()
            print(f"✓ Repository created!")
            print(f"  URL: {repo_data['html_url']}")
            print(f"  Clone: {repo_data['clone_url']}")
            
            return {
                "success": True,
                "repo_url": repo_data['html_url'],
                "clone_url": repo_data['clone_url'],
                "full_name": repo_data['full_name']
            }
        else:
            error = response.json().get('message', 'Unknown error')
            print(f"✗ Failed: {error}")
            return {"success": False, "error": error}
    
    def list_repositories(self) -> List[Dict[str, Any]]:
        """List all your repositories"""
        response = requests.get(
            f"{self.base_url}/user/repos",
            headers=self.headers,
            params={"per_page": 100}
        )
        
        if response.status_code == 200:
            repos = response.json()
            return [
                {
                    "name": repo["name"],
                    "url": repo["html_url"],
                    "private": repo["private"]
                }
                for repo in repos
            ]
        return []
    
    def delete_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """Delete a repository (use with caution!)"""
        response = requests.delete(
            f"{self.base_url}/repos/{owner}/{repo}",
            headers=self.headers
        )
        
        if response.status_code == 204:
            return {"success": True}
        else:
            return {"success": False, "error": response.json().get('message')}


# Quick usage example
if __name__ == "__main__":
    print("=" * 60)
    print("GitHub Connector - Quick Setup")
    print("=" * 60)
    
    try:
        # Initialize connector
        github = GitHubConnector()
        
        print(f"\n✓ Connected as: {github.username}")
        
        # Example: Create repository
        result = github.create_repository(
            name="AI-Agentic-Framework",
            description="AI Agentic Framework with Constitutional AI",
            private=False
        )
        
        if result["success"]:
            print("\n🎉 Success! Repository created!")
            print(f"\nNext steps:")
            print(f"1. cd F:\\AI-Agentic-Framework")
            print(f"2. git init")
            print(f"3. git add .")
            print(f"4. git commit -m 'Initial commit'")
            print(f"5. git remote add origin {result['clone_url']}")
            print(f"6. git push -u origin main")
        
    except ValueError as e:
        print(f"\n❌ {e}")
