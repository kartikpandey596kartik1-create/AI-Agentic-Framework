"""
Google Drive Connector - Complete Google Drive API Integration
Supports file upload, download, search, sharing, and folder management
"""

import os
import io
import json
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

# Note: Requires google-auth and google-api-python-client
# pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

class GoogleDriveConnector:
    """
    Complete Google Drive API connector
    """
    
    SCOPES = ['https://www.googleapis.com/auth/drive']
    
    def __init__(self, credentials_path: str = 'credentials.json', token_path: str = 'token.json'):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self.logger = logging.getLogger(__name__)
        
        if not GOOGLE_AVAILABLE:
            self.logger.error("Google API libraries not installed. Run: pip install google-auth google-api-python-client")
            return
        
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Drive API"""
        creds = None
        
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    self.logger.error(f"Credentials file not found: {self.credentials_path}")
                    self.logger.info("Download credentials from Google Cloud Console")
                    return
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('drive', 'v3', credentials=creds)
        self.logger.info("Google Drive authenticated successfully")
    
    def upload_file(
        self,
        file_path: str,
        folder_id: Optional[str] = None,
        mime_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Upload a file to Google Drive"""
        if not self.service:
            return {"error": "Not authenticated"}
        
        file_metadata = {'name': os.path.basename(file_path)}
        
        if folder_id:
            file_metadata['parents'] = [folder_id]
        
        media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
        
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, mimeType, webViewLink'
        ).execute()
        
        self.logger.info(f"File uploaded: {file.get('name')} (ID: {file.get('id')})")
        return file
    
    def download_file(self, file_id: str, destination_path: str) -> bool:
        """Download a file from Google Drive"""
        if not self.service:
            return False
        
        request = self.service.files().get_media(fileId=file_id)
        
        fh = io.FileIO(destination_path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        
        done = False
        while not done:
            status, done = downloader.next_chunk()
            self.logger.info(f"Download {int(status.progress() * 100)}%")
        
        self.logger.info(f"File downloaded to {destination_path}")
        return True
    
    def create_folder(self, folder_name: str, parent_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a folder in Google Drive"""
        if not self.service:
            return {"error": "Not authenticated"}
        
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        if parent_id:
            file_metadata['parents'] = [parent_id]
        
        folder = self.service.files().create(
            body=file_metadata,
            fields='id, name, webViewLink'
        ).execute()
        
        self.logger.info(f"Folder created: {folder.get('name')} (ID: {folder.get('id')})")
        return folder
    
    def list_files(
        self,
        folder_id: Optional[str] = None,
        query: Optional[str] = None,
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """List files in Google Drive"""
        if not self.service:
            return []
        
        if query is None:
            query = "trashed=false"
            if folder_id:
                query += f" and '{folder_id}' in parents"
        
        results = self.service.files().list(
            q=query,
            pageSize=max_results,
            fields="files(id, name, mimeType, createdTime, modifiedTime, size, webViewLink)"
        ).execute()
        
        return results.get('files', [])
    
    def search_files(self, search_term: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """Search for files by name"""
        query = f"name contains '{search_term}' and trashed=false"
        return self.list_files(query=query, max_results=max_results)
    
    def delete_file(self, file_id: str, permanent: bool = False) -> bool:
        """Delete a file (move to trash or permanent)"""
        if not self.service:
            return False
        
        try:
            if permanent:
                self.service.files().delete(fileId=file_id).execute()
            else:
                self.service.files().update(
                    fileId=file_id,
                    body={'trashed': True}
                ).execute()
            
            self.logger.info(f"File deleted: {file_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete file: {e}")
            return False
    
    def share_file(
        self,
        file_id: str,
        email: Optional[str] = None,
        role: str = 'reader',
        type: str = 'user'
    ) -> Dict[str, Any]:
        """
        Share a file with user or make it public
        
        role: 'reader', 'writer', 'commenter', 'owner'
        type: 'user', 'anyone'
        """
        if not self.service:
            return {"error": "Not authenticated"}
        
        permission = {
            'type': type,
            'role': role
        }
        
        if email and type == 'user':
            permission['emailAddress'] = email
        
        result = self.service.permissions().create(
            fileId=file_id,
            body=permission,
            fields='id'
        ).execute()
        
        self.logger.info(f"File shared: {file_id}")
        return result
    
    def get_file_info(self, file_id: str) -> Dict[str, Any]:
        """Get detailed file information"""
        if not self.service:
            return {"error": "Not authenticated"}
        
        file = self.service.files().get(
            fileId=file_id,
            fields='*'
        ).execute()
        
        return file
    
    def copy_file(self, file_id: str, new_name: str) -> Dict[str, Any]:
        """Copy a file"""
        if not self.service:
            return {"error": "Not authenticated"}
        
        body = {'name': new_name}
        
        copied_file = self.service.files().copy(
            fileId=file_id,
            body=body
        ).execute()
        
        self.logger.info(f"File copied: {copied_file.get('name')}")
        return copied_file
    
    def move_file(self, file_id: str, new_parent_id: str) -> Dict[str, Any]:
        """Move a file to a different folder"""
        if not self.service:
            return {"error": "Not authenticated"}
        
        # Get current parents
        file = self.service.files().get(
            fileId=file_id,
            fields='parents'
        ).execute()
        
        previous_parents = ",".join(file.get('parents'))
        
        # Move file
        file = self.service.files().update(
            fileId=file_id,
            addParents=new_parent_id,
            removeParents=previous_parents,
            fields='id, parents'
        ).execute()
        
        self.logger.info(f"File moved: {file_id}")
        return file
    
    def upload_folder(self, folder_path: str, parent_id: Optional[str] = None) -> Dict[str, Any]:
        """Upload an entire folder recursively"""
        if not self.service:
            return {"error": "Not authenticated"}
        
        folder_name = os.path.basename(folder_path)
        
        # Create root folder
        root_folder = self.create_folder(folder_name, parent_id)
        root_folder_id = root_folder['id']
        
        uploaded_files = []
        
        # Upload all files
        for root, dirs, files in os.walk(folder_path):
            # Create subdirectories
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                relative_path = os.path.relpath(dir_path, folder_path)
                
                subfolder = self.create_folder(dir_name, root_folder_id)
                uploaded_files.append(subfolder)
            
            # Upload files
            for file_name in files:
                file_path = os.path.join(root, file_name)
                
                uploaded_file = self.upload_file(file_path, root_folder_id)
                uploaded_files.append(uploaded_file)
        
        return {
            "folder": root_folder,
            "uploaded_count": len(uploaded_files),
            "files": uploaded_files
        }
    
    def get_storage_quota(self) -> Dict[str, Any]:
        """Get storage quota information"""
        if not self.service:
            return {"error": "Not authenticated"}
        
        about = self.service.about().get(fields='storageQuota, user').execute()
        
        quota = about.get('storageQuota', {})
        
        return {
            "limit": int(quota.get('limit', 0)),
            "usage": int(quota.get('usage', 0)),
            "usage_in_drive": int(quota.get('usageInDrive', 0)),
            "usage_in_trash": int(quota.get('usageInDriveTrash', 0)),
            "user": about.get('user', {}).get('emailAddress', 'Unknown')
        }


# Example usage
if __name__ == "__main__":
    # Initialize connector
    # drive = GoogleDriveConnector()
    
    # Upload file
    # file = drive.upload_file("document.pdf")
    
    # Search files
    # files = drive.search_files("project")
    
    # Create folder
    # folder = drive.create_folder("My Projects")
    
    print("Google Drive Connector ready!")
    print("Note: Requires credentials.json from Google Cloud Console")
