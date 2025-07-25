"""
GitHub API integration for fetching real-time profile and repository data.
"""
import requests
from datetime import datetime
from typing import Dict, List, Optional
import os


class GitHubAPI:
    """GitHub API client for fetching user profile and repository data."""
    
    def __init__(self, username: str, token: Optional[str] = None):
        """
        Initialize GitHub API client.
        
        Args:
            username: GitHub username
            token: Optional GitHub personal access token for higher rate limits
        """
        self.username = username
        self.base_url = "https://api.github.com"
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        
        # Add authentication if token is provided
        if token:
            self.headers["Authorization"] = f"token {token}"
        elif os.getenv("GITHUB_TOKEN"):
            self.headers["Authorization"] = f"token {os.getenv('GITHUB_TOKEN')}"
    
    def get_user_profile(self) -> Dict:
        """Get user profile information."""
        try:
            response = requests.get(f"{self.base_url}/users/{self.username}", headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching user profile: {e}")
            return {}
    
    def get_repositories(self, sort: str = "updated", per_page: int = 30) -> List[Dict]:
        """
        Get user repositories.
        
        Args:
            sort: Sort repositories by 'created', 'updated', 'pushed', 'full_name'
            per_page: Number of repositories per page (max 100)
        """
        try:
            params = {"sort": sort, "per_page": per_page, "type": "owner"}
            response = requests.get(
                f"{self.base_url}/users/{self.username}/repos", 
                headers=self.headers, 
                params=params
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching repositories: {e}")
            return []
    
    def get_repository_languages(self, repo_name: str) -> Dict[str, int]:
        """Get programming languages used in a specific repository."""
        try:
            response = requests.get(
                f"{self.base_url}/repos/{self.username}/{repo_name}/languages",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching languages for {repo_name}: {e}")
            return {}
    
    def get_user_activity(self) -> List[Dict]:
        """Get recent user activity events."""
        try:
            response = requests.get(
                f"{self.base_url}/users/{self.username}/events/public",
                headers=self.headers,
                params={"per_page": 10}
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching user activity: {e}")
            return []
    
    def get_comprehensive_profile(self) -> Dict:
        """Get comprehensive profile data including repositories and language stats."""
        print("Fetching GitHub profile data...")
        
        # Get basic profile
        profile = self.get_user_profile()
        if not profile:
            return {"error": "Could not fetch GitHub profile"}
        
        # Get repositories
        repos = self.get_repositories()
        
        # Calculate language statistics across all repos
        language_stats = {}
        total_bytes = 0
        featured_repos = []
        
        for repo in repos:
            if not repo.get('fork', False):  # Skip forked repositories
                # Get languages for this repo
                languages = self.get_repository_languages(repo['name'])
                
                # Add to overall stats
                for lang, bytes_count in languages.items():
                    language_stats[lang] = language_stats.get(lang, 0) + bytes_count
                    total_bytes += bytes_count
                
                # Add to featured repos if it has stars or is not a fork
                if repo.get('stargazers_count', 0) > 0 or repo.get('description'):
                    featured_repos.append({
                        'name': repo['name'],
                        'description': repo.get('description', ''),
                        'html_url': repo['html_url'],
                        'stargazers_count': repo.get('stargazers_count', 0),
                        'forks_count': repo.get('forks_count', 0),
                        'language': repo.get('language'),
                        'updated_at': repo.get('updated_at'),
                        'topics': repo.get('topics', [])
                    })
        
        # Calculate language percentages
        language_percentages = {}
        if total_bytes > 0:
            for lang, bytes_count in language_stats.items():
                language_percentages[lang] = round((bytes_count / total_bytes) * 100, 1)
        
        # Sort featured repos by stars and recency
        featured_repos.sort(key=lambda x: (x['stargazers_count'], x['updated_at']), reverse=True)
        
        # Get recent activity
        recent_activity = self.get_user_activity()
        
        return {
            'profile': {
                'name': profile.get('name', self.username),
                'bio': profile.get('bio', ''),
                'location': profile.get('location', ''),
                'blog': profile.get('blog', ''),
                'company': profile.get('company', ''),
                'email': profile.get('email', ''),
                'twitter_username': profile.get('twitter_username', ''),
                'public_repos': profile.get('public_repos', 0),
                'followers': profile.get('followers', 0),
                'following': profile.get('following', 0),
                'created_at': profile.get('created_at', ''),
                'updated_at': profile.get('updated_at', ''),
                'html_url': profile.get('html_url', '')
            },
            'repositories': {
                'total_count': len(repos),
                'featured': featured_repos[:10],  # Top 10 featured repos
                'recent': repos[:5]  # 5 most recently updated
            },
            'languages': {
                'stats': language_percentages,
                'top_languages': sorted(language_percentages.items(), key=lambda x: x[1], reverse=True)[:5]
            },
            'activity': {
                'recent_events': recent_activity[:5],
                'last_updated': datetime.now().isoformat()
            }
        }
    
    def format_for_llm(self, data: Dict) -> str:
        """Format GitHub data for LLM consumption."""
        if 'error' in data:
            return f"GitHub data unavailable: {data['error']}"
        
        profile = data.get('profile', {})
        repos = data.get('repositories', {})
        languages = data.get('languages', {})
        
        # Build formatted string
        sections = []
        
        # Profile section
        if profile:
            profile_section = f"## GitHub Profile\n"
            profile_section += f"- **Name**: {profile.get('name', 'N/A')}\n"
            if profile.get('bio'):
                profile_section += f"- **Bio**: {profile['bio']}\n"
            if profile.get('location'):
                profile_section += f"- **Location**: {profile['location']}\n"
            if profile.get('company'):
                profile_section += f"- **Company**: {profile['company']}\n"
            profile_section += f"- **Public Repositories**: {profile.get('public_repos', 0)}\n"
            profile_section += f"- **Followers**: {profile.get('followers', 0)}\n"
            profile_section += f"- **Profile**: {profile.get('html_url', '')}\n"
            sections.append(profile_section)
        
        # Programming languages
        if languages.get('top_languages'):
            lang_section = "## Programming Languages\n"
            for lang, percentage in languages['top_languages']:
                lang_section += f"- **{lang}**: {percentage}%\n"
            sections.append(lang_section)
        
        # Featured repositories
        if repos.get('featured'):
            repos_section = "## Featured Projects\n"
            for repo in repos['featured'][:5]:  # Top 5
                repos_section += f"### {repo['name']}\n"
                if repo.get('description'):
                    repos_section += f"{repo['description']}\n"
                repos_section += f"- **Language**: {repo.get('language', 'N/A')}\n"
                repos_section += f"- **Stars**: {repo.get('stargazers_count', 0)}\n"
                repos_section += f"- **URL**: {repo.get('html_url', '')}\n"
                if repo.get('topics'):
                    repos_section += f"- **Topics**: {', '.join(repo['topics'])}\n"
                repos_section += "\n"
            sections.append(repos_section)
        
        return "\n".join(sections)


def get_github_data_for_user(username: str, token: Optional[str] = None) -> str:
    """
    Convenience function to get formatted GitHub data for a user.
    
    Args:
        username: GitHub username
        token: Optional GitHub token
        
    Returns:
        Formatted string suitable for LLM context
    """
    github_api = GitHubAPI(username, token)
    data = github_api.get_comprehensive_profile()
    return github_api.format_for_llm(data)


# Example usage and testing
if __name__ == "__main__":
    # Test the GitHub API integration
    username = "adrianmf94"
    github_data = get_github_data_for_user(username)
    print(f"GitHub integration test successful. Data length: {len(github_data)} characters") 