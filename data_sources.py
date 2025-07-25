"""
Data sources manager for the LLM Alter Ego chatbot.
Combines PDF, summary text, and GitHub API data sources.
"""
import os
from datetime import datetime
from typing import Dict, Optional
from pypdf import PdfReader

from github_api import get_github_data_for_user


class DataSourceManager:
    """Manages and combines data from PDF, summary, and GitHub sources."""
    
    def __init__(self, config: Dict):
        """
        Initialize data source manager.
        
        Args:
            config: Configuration dictionary with source settings
        """
        self.config = config
        self.cache = {}
        self.last_updated = {}
    
    def load_pdf_content(self) -> str:
        """Load LinkedIn PDF content."""
        linkedin_path = self.config.get("linkedin_pdf_path", "me/linkedin.pdf")
        if not os.path.exists(linkedin_path):
            return ""
        
        try:
            reader = PdfReader(linkedin_path)
            linkedin_text = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    linkedin_text += text
            return linkedin_text
        except Exception as e:
            print(f"Error reading LinkedIn PDF: {e}")
            return ""
    
    def load_summary_content(self) -> str:
        """Load summary text content."""
        summary_path = self.config.get("summary_path", "me/summary.txt")
        if not os.path.exists(summary_path):
            return ""
        
        try:
            with open(summary_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception as e:
            print(f"Error reading summary file: {e}")
            return ""
    
    def get_github_data(self, force_refresh: bool = False) -> str:
        """Get GitHub data with caching."""
        cache_key = "github_data"
        cache_duration = self.config.get("github_cache_duration", 3600)  # 1 hour default
        
        # Check cache
        if not force_refresh and cache_key in self.cache:
            last_update = self.last_updated.get(cache_key, datetime.min)
            if (datetime.now() - last_update).seconds < cache_duration:
                return self.cache[cache_key]
        
        # Fetch fresh data
        github_username = self.config.get("github_username")
        github_token = self.config.get("github_token")
        
        if not github_username:
            return ""
        
        try:
            github_data = get_github_data_for_user(github_username, github_token)
            self.cache[cache_key] = github_data
            self.last_updated[cache_key] = datetime.now()
            return github_data
        except Exception as e:
            print(f"Error fetching GitHub data: {e}")
            return ""
    
    def get_comprehensive_profile(self, include_github: bool = True) -> str:
        """Get comprehensive profile combining all data sources."""
        sections = []
        
        # Add summary
        summary = self.load_summary_content()
        if summary:
            sections.append(f"## Summary\n{summary}")
        
        # Add LinkedIn data
        linkedin_content = self.load_pdf_content()
        if linkedin_content:
            sections.append(f"## LinkedIn Profile\n{linkedin_content}")
        
        # Add GitHub data
        if include_github and self.config.get("github_username"):
            github_data = self.get_github_data()
            if github_data:
                sections.append(github_data)
        
        return "\n\n".join(sections)


def create_default_config() -> Dict:
    """Create default configuration for data sources."""
    return {
        "name": "Adrian Monge",
        "github_username": "adrianmf94",  # GitHub username for API integration
        "github_token": None,  # Optional: Set via environment variable GITHUB_TOKEN for higher rate limits
        "linkedin_pdf_path": "me/linkedin.pdf",
        "summary_path": "me/summary.txt",
        "github_cache_duration": 3600,  # 1 hour in seconds
        "prompt_style": "main",  # Options: "main", "professional", "casual"
    }


# Example usage and testing
if __name__ == "__main__":
    config = create_default_config()
    dsm = DataSourceManager(config)
    
    # Test individual components
    print("="*50)
    print("TESTING INDIVIDUAL COMPONENTS")
    print("="*50)
    
    print("\n1. Summary Content:")
    summary = dsm.load_summary_content()
    print(f"Length: {len(summary)} characters")
    if summary:
        print(f"Preview: {summary[:100]}...")
    
    print("\n2. LinkedIn PDF Content:")
    linkedin = dsm.load_pdf_content()
    print(f"Length: {len(linkedin)} characters")
    if linkedin:
        print(f"Preview: {linkedin[:100]}...")
    
    print("\n3. GitHub Data:")
    github = dsm.get_github_data()
    print(f"Length: {len(github)} characters")
    if github:
        print(f"Preview: {github[:200]}...")
    
    # Get comprehensive profile
    print("\n" + "="*50)
    print("COMPREHENSIVE PROFILE")
    print("="*50)
    profile = dsm.get_comprehensive_profile()
    print(f"Total length: {len(profile)} characters")
    print("\nFull content:")
    print(profile) 