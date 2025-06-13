"""
GitHub API Client

This module provides functionality to interact with the GitHub API
and fetch user activity data.
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union

import requests
from github import Github
from github.GithubException import GithubException

logger = logging.getLogger(__name__)


class GitHubClient:
    """Client for interacting with the GitHub API."""

    def __init__(self, token: Optional[str] = None, config_path: Optional[str] = None):
        """
        Initialize the GitHub client.

        Args:
            token: GitHub API token. If not provided, will look for it in config file.
            config_path: Path to the configuration file. Defaults to 'config/config.json'.
        """
        self.token = token
        self.config_path = config_path or os.path.join("config", "config.json")
        self.config = self._load_config()

        if not self.token:
            self.token = self.config.get("github", {}).get("api_token")

        if not self.token or self.token == "YOUR_GITHUB_PERSONAL_ACCESS_TOKEN":
            raise ValueError(
                "GitHub API token not provided. Please set it in the config file or pass it directly."
            )

        self.github = Github(self.token)
        self.api_url = self.config.get("github", {}).get("api_url", "https://api.github.com")
        self.user_agent = self.config.get("github", {}).get("user_agent", "GitHub-Activities-Tracker")

    def _load_config(self) -> Dict:
        """Load configuration from file."""
        try:
            with open(self.config_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found at {self.config_path}. Using default configuration.")
            return {}
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in config file {self.config_path}. Using default configuration.")
            return {}

    def get_user(self, username: str):
        """
        Get a GitHub user by username.

        Args:
            username: The GitHub username.

        Returns:
            The GitHub user object.
        """
        try:
            return self.github.get_user(username)
        except GithubException as e:
            logger.error(f"Error fetching user {username}: {e}")
            raise

    def get_user_commits(self, username: str, since: Optional[datetime] = None, 
                         until: Optional[datetime] = None, repository: Optional[str] = None) -> List[Dict]:
        """
        Get commits made by a user.

        Args:
            username: The GitHub username.
            since: Start date for commit search.
            until: End date for commit search.
            repository: Repository name to filter by (e.g., "owner/repo").

        Returns:
            List of commit data.
        """
        if not since:
            since = datetime.now() - timedelta(days=365)
        if not until:
            until = datetime.now()

        query = f"author:{username} committer-date:{since.strftime('%Y-%m-%d')}..{until.strftime('%Y-%m-%d')}"
        if repository:
            query += f" repo:{repository}"
        commits = []

        try:
            search_result = self.github.search_commits(query=query)
            for commit in search_result:
                # Extract repository name from the HTML URL
                # URL format: https://github.com/owner/repo/commit/sha
                repo_name = "/".join(commit.html_url.split("/")[3:5]) if commit.html_url else "Unknown"

                commits.append({
                    "sha": commit.sha,
                    "message": commit.commit.message,
                    "date": commit.commit.author.date.isoformat(),
                    "repository": repo_name,
                    "url": commit.html_url
                })
            return commits
        except GithubException as e:
            logger.error(f"Error fetching commits for user {username}: {e}")
            return []

    def get_user_pull_requests(self, username: str, state: str = "all",
                              since: Optional[datetime] = None,
                              until: Optional[datetime] = None,
                              repository: Optional[str] = None) -> List[Dict]:
        """
        Get pull requests created by a user.

        Args:
            username: The GitHub username.
            state: PR state (open, closed, all).
            since: Start date for PR search.
            until: End date for PR search.
            repository: Repository name to filter by (e.g., "owner/repo").

        Returns:
            List of pull request data.
        """
        if not since:
            since = datetime.now() - timedelta(days=365)
        if not until:
            until = datetime.now()

        query = f"author:{username} created:{since.strftime('%Y-%m-%d')}..{until.strftime('%Y-%m-%d')}"
        if repository:
            query += f" repo:{repository}"
        pull_requests = []

        try:
            search_result = self.github.search_issues(query=query, sort="created", order="desc")
            for issue in search_result:
                if not hasattr(issue, "pull_request") or not issue.pull_request:
                    continue

                pull_requests.append({
                    "number": issue.number,
                    "title": issue.title,
                    "state": issue.state,
                    "created_at": issue.created_at.isoformat(),
                    "updated_at": issue.updated_at.isoformat(),
                    "closed_at": issue.closed_at.isoformat() if issue.closed_at else None,
                    "repository": issue.repository.full_name,
                    "url": issue.html_url
                })
            return pull_requests
        except GithubException as e:
            logger.error(f"Error fetching pull requests for user {username}: {e}")
            return []

    def get_user_issues(self, username: str, state: str = "all",
                       since: Optional[datetime] = None,
                       until: Optional[datetime] = None,
                       repository: Optional[str] = None) -> List[Dict]:
        """
        Get issues created by a user.

        Args:
            username: The GitHub username.
            state: Issue state (open, closed, all).
            since: Start date for issue search.
            until: End date for issue search.
            repository: Repository name to filter by (e.g., "owner/repo").

        Returns:
            List of issue data.
        """
        if not since:
            since = datetime.now() - timedelta(days=365)
        if not until:
            until = datetime.now()

        query = f"author:{username} is:issue created:{since.strftime('%Y-%m-%d')}..{until.strftime('%Y-%m-%d')}"
        if repository:
            query += f" repo:{repository}"
        issues = []

        try:
            search_result = self.github.search_issues(query=query, sort="created", order="desc")
            for issue in search_result:
                if hasattr(issue, "pull_request") and issue.pull_request:
                    continue

                issues.append({
                    "number": issue.number,
                    "title": issue.title,
                    "state": issue.state,
                    "created_at": issue.created_at.isoformat(),
                    "updated_at": issue.updated_at.isoformat(),
                    "closed_at": issue.closed_at.isoformat() if issue.closed_at else None,
                    "repository": issue.repository.full_name,
                    "url": issue.html_url
                })
            return issues
        except GithubException as e:
            logger.error(f"Error fetching issues for user {username}: {e}")
            return []

    def get_user_reviews(self, username: str, since: Optional[datetime] = None,
                        until: Optional[datetime] = None,
                        repository: Optional[str] = None) -> List[Dict]:
        """
        Get code reviews done by a user.

        Args:
            username: The GitHub username.
            since: Start date for review search.
            until: End date for review search.
            repository: Repository name to filter by (e.g., "owner/repo").

        Returns:
            List of review data.
        """
        # This requires using the REST API directly as PyGithub doesn't have a direct method
        if not since:
            since = datetime.now() - timedelta(days=365)
        if not until:
            until = datetime.now()

        # This is a simplified approach - in a real app, you'd need to handle pagination
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": self.user_agent
        }

        query = f"q=reviewed-by:{username}+updated:{since.strftime('%Y-%m-%d')}..{until.strftime('%Y-%m-%d')}"
        if repository:
            query += f"+repo:{repository}"
        url = f"{self.api_url}/search/issues?{query}"

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            reviews = []
            for item in data.get("items", []):
                if "pull_request" not in item:
                    continue

                reviews.append({
                    "pr_number": item["number"],
                    "pr_title": item["title"],
                    "repository": item["repository_url"].split("/")[-2] + "/" + item["repository_url"].split("/")[-1],
                    "reviewed_at": item["updated_at"],
                    "url": item["html_url"]
                })

            return reviews
        except requests.RequestException as e:
            logger.error(f"Error fetching reviews for user {username}: {e}")
            return []

    def _aggregate_by_period(self, data, period_type):
        """
        Aggregate data by week or month.

        Args:
            data: List of dictionaries containing activity data.
            period_type: 'week' or 'month'.

        Returns:
            Dictionary with aggregated data by period.
        """
        aggregated = {}
        date_format = "%Y-W%W" if period_type == 'week' else "%Y-%m"

        for item in data:
            # Determine the date field based on the item structure
            if 'date' in item:
                date_str = item['date']
            elif 'created_at' in item:
                date_str = item['created_at']
            elif 'reviewed_at' in item:
                date_str = item['reviewed_at']
            else:
                continue

            # Parse the date
            try:
                date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                period_key = date.strftime(date_format)

                if period_key not in aggregated:
                    aggregated[period_key] = 0
                aggregated[period_key] += 1
            except (ValueError, TypeError):
                continue

        # Convert to sorted list of tuples
        result = [(k, v) for k, v in aggregated.items()]
        result.sort(key=lambda x: x[0])

        return result

    def get_user_activity_summary(self, username: str, since: Optional[datetime] = None,
                                 until: Optional[datetime] = None,
                                 repository: Optional[str] = None,
                                 aggregation: Optional[str] = None) -> Dict:
        """
        Get a summary of user activity.

        Args:
            username: The GitHub username.
            since: Start date for activity search.
            until: End date for activity search.
            repository: Repository name to filter by (e.g., "owner/repo").
            aggregation: Type of aggregation ('week', 'month', or None for no aggregation).

        Returns:
            Dictionary with activity summary.
        """
        if not since:
            since = datetime.now() - timedelta(days=365)
        if not until:
            until = datetime.now()

        commits = self.get_user_commits(username, since, until, repository)
        pull_requests = self.get_user_pull_requests(username, "all", since, until, repository)
        issues = self.get_user_issues(username, "all", since, until, repository)
        reviews = self.get_user_reviews(username, since, until, repository)

        # Get user profile info
        user = self.get_user(username)

        result = {
            "user": {
                "login": user.login,
                "name": user.name,
                "avatar_url": user.avatar_url,
                "html_url": user.html_url,
                "public_repos": user.public_repos,
                "followers": user.followers,
                "following": user.following,
                "created_at": user.created_at.isoformat(),
            },
            "activity_period": {
                "since": since.isoformat(),
                "until": until.isoformat(),
                "days": (until - since).days
            },
            "summary": {
                "commits_count": len(commits),
                "pull_requests_count": len(pull_requests),
                "issues_count": len(issues),
                "reviews_count": len(reviews),
                "total_contributions": len(commits) + len(pull_requests) + len(issues) + len(reviews)
            },
            "details": {
                "commits": commits[:5],  # Just include the first 5 for brevity
                "pull_requests": pull_requests[:5],
                "issues": issues[:5],
                "reviews": reviews[:5]
            }
        }

        # Add aggregated data if requested
        if aggregation in ('week', 'month'):
            result["aggregated"] = {
                "commits": self._aggregate_by_period(commits, aggregation),
                "pull_requests": self._aggregate_by_period(pull_requests, aggregation),
                "issues": self._aggregate_by_period(issues, aggregation),
                "reviews": self._aggregate_by_period(reviews, aggregation)
            }

        return result
