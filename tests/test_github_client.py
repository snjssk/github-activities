"""
Tests for the GitHub API client.

These tests use pytest and mock the GitHub API responses
to avoid making actual API calls during testing.
"""

import json
import os
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from github.GithubException import GithubException

from github_activities.github_client import GitHubClient


@pytest.fixture
def mock_config():
    """Create a mock configuration for testing."""
    return {
        "github": {
            "api_token": "mock_token",
            "api_url": "https://api.github.com",
            "user_agent": "GitHub-Activities-Tracker-Test"
        }
    }


@pytest.fixture
def mock_github_client(mock_config):
    """Create a mock GitHub client for testing."""
    with patch("github_activities.github_client.Github") as mock_github:
        client = GitHubClient(token="mock_token")
        client.config = mock_config
        client.github = mock_github
        yield client


def test_init_with_token():
    """Test initializing the client with a token."""
    with patch("github_activities.github_client.Github") as mock_github:
        client = GitHubClient(token="test_token")
        assert client.token == "test_token"
        mock_github.assert_called_once_with("test_token")


def test_init_without_token():
    """Test initializing the client without a token raises an error."""
    with patch("github_activities.github_client.os.path.join", return_value="mock_path"), \
         patch("github_activities.github_client.GitHubClient._load_config", return_value={}):
        with pytest.raises(ValueError):
            GitHubClient()


def test_get_user(mock_github_client):
    """Test getting a user."""
    mock_user = MagicMock()
    mock_user.login = "octocat"
    mock_user.name = "The Octocat"
    mock_github_client.github.get_user.return_value = mock_user
    
    user = mock_github_client.get_user("octocat")
    
    mock_github_client.github.get_user.assert_called_once_with("octocat")
    assert user.login == "octocat"
    assert user.name == "The Octocat"


def test_get_user_error(mock_github_client):
    """Test error handling when getting a user."""
    mock_github_client.github.get_user.side_effect = GithubException(404, "Not Found")
    
    with pytest.raises(GithubException):
        mock_github_client.get_user("nonexistent_user")


def test_get_user_commits(mock_github_client):
    """Test getting user commits."""
    # Create mock search result
    mock_commit1 = MagicMock()
    mock_commit1.sha = "abc123"
    mock_commit1.commit.message = "Test commit"
    mock_commit1.commit.author.date = datetime.now()
    mock_commit1.repository.full_name = "octocat/Hello-World"
    mock_commit1.html_url = "https://github.com/octocat/Hello-World/commit/abc123"
    
    mock_search_result = MagicMock()
    mock_search_result.__iter__.return_value = [mock_commit1]
    mock_github_client.github.search_commits.return_value = mock_search_result
    
    # Call the method
    commits = mock_github_client.get_user_commits("octocat")
    
    # Verify the result
    assert len(commits) == 1
    assert commits[0]["sha"] == "abc123"
    assert commits[0]["message"] == "Test commit"
    assert commits[0]["repository"] == "octocat/Hello-World"


def test_get_user_pull_requests(mock_github_client):
    """Test getting user pull requests."""
    # Create mock search result
    mock_pr = MagicMock()
    mock_pr.number = 1
    mock_pr.title = "Test PR"
    mock_pr.state = "open"
    mock_pr.created_at = datetime.now()
    mock_pr.updated_at = datetime.now()
    mock_pr.closed_at = None
    mock_pr.repository.full_name = "octocat/Hello-World"
    mock_pr.html_url = "https://github.com/octocat/Hello-World/pull/1"
    mock_pr.pull_request = True  # This is what identifies it as a PR
    
    mock_search_result = MagicMock()
    mock_search_result.__iter__.return_value = [mock_pr]
    mock_github_client.github.search_issues.return_value = mock_search_result
    
    # Call the method
    prs = mock_github_client.get_user_pull_requests("octocat")
    
    # Verify the result
    assert len(prs) == 1
    assert prs[0]["number"] == 1
    assert prs[0]["title"] == "Test PR"
    assert prs[0]["state"] == "open"
    assert prs[0]["repository"] == "octocat/Hello-World"


def test_get_user_issues(mock_github_client):
    """Test getting user issues."""
    # Create mock search result
    mock_issue = MagicMock()
    mock_issue.number = 1
    mock_issue.title = "Test Issue"
    mock_issue.state = "open"
    mock_issue.created_at = datetime.now()
    mock_issue.updated_at = datetime.now()
    mock_issue.closed_at = None
    mock_issue.repository.full_name = "octocat/Hello-World"
    mock_issue.html_url = "https://github.com/octocat/Hello-World/issues/1"
    mock_issue.pull_request = None  # This is what identifies it as an issue, not a PR
    
    mock_search_result = MagicMock()
    mock_search_result.__iter__.return_value = [mock_issue]
    mock_github_client.github.search_issues.return_value = mock_search_result
    
    # Call the method
    issues = mock_github_client.get_user_issues("octocat")
    
    # Verify the result
    assert len(issues) == 1
    assert issues[0]["number"] == 1
    assert issues[0]["title"] == "Test Issue"
    assert issues[0]["state"] == "open"
    assert issues[0]["repository"] == "octocat/Hello-World"


def test_get_user_reviews(mock_github_client):
    """Test getting user reviews."""
    # Mock the requests.get response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "items": [
            {
                "number": 1,
                "title": "Test PR",
                "repository_url": "https://api.github.com/repos/octocat/Hello-World",
                "updated_at": "2023-01-01T00:00:00Z",
                "html_url": "https://github.com/octocat/Hello-World/pull/1",
                "pull_request": {}  # This indicates it's a PR
            }
        ]
    }
    mock_response.raise_for_status = MagicMock()
    
    with patch("github_activities.github_client.requests.get", return_value=mock_response):
        # Call the method
        reviews = mock_github_client.get_user_reviews("octocat")
        
        # Verify the result
        assert len(reviews) == 1
        assert reviews[0]["pr_number"] == 1
        assert reviews[0]["pr_title"] == "Test PR"
        assert reviews[0]["repository"] == "octocat/Hello-World"
        assert reviews[0]["url"] == "https://github.com/octocat/Hello-World/pull/1"


def test_get_user_activity_summary(mock_github_client):
    """Test getting user activity summary."""
    # Mock the individual methods
    mock_github_client.get_user_commits = MagicMock(return_value=[{"sha": "abc123"}])
    mock_github_client.get_user_pull_requests = MagicMock(return_value=[{"number": 1}])
    mock_github_client.get_user_issues = MagicMock(return_value=[{"number": 2}])
    mock_github_client.get_user_reviews = MagicMock(return_value=[{"pr_number": 3}])
    
    # Mock the user
    mock_user = MagicMock()
    mock_user.login = "octocat"
    mock_user.name = "The Octocat"
    mock_user.avatar_url = "https://github.com/octocat.png"
    mock_user.html_url = "https://github.com/octocat"
    mock_user.public_repos = 10
    mock_user.followers = 100
    mock_user.following = 50
    mock_user.created_at = datetime.now()
    mock_github_client.get_user = MagicMock(return_value=mock_user)
    
    # Call the method
    summary = mock_github_client.get_user_activity_summary("octocat")
    
    # Verify the result
    assert summary["user"]["login"] == "octocat"
    assert summary["user"]["name"] == "The Octocat"
    assert summary["summary"]["commits_count"] == 1
    assert summary["summary"]["pull_requests_count"] == 1
    assert summary["summary"]["issues_count"] == 1
    assert summary["summary"]["reviews_count"] == 1
    assert summary["summary"]["total_contributions"] == 4