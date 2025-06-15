# GitHub Activities Tracker Documentation

## Overview

GitHub Activities Tracker is a command-line tool that fetches and displays GitHub user activities including:
- Commit counts
- Pull request numbers
- Issue creation counts
- Code review counts
- Other GitHub activity metrics

## Installation

### Prerequisites
- Python 3.8 or higher
- GitHub Personal Access Token with appropriate permissions

### Installing from source
```bash
# Clone the repository
git clone https://github.com/yourusername/github-activities.git
cd github-activities

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`

# Update pip and install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Install the package
pip install -e .

# When you're done, you can deactivate the virtual environment
# deactivate
```

## Configuration

Before using the tool, you need to set up your GitHub API token. You can do this in two ways:

### Using the setup command
```bash
github-activities setup
```
This interactive command will prompt you for your GitHub API token and create a configuration file.

### Manual configuration
1. Copy the template configuration file:
```bash
cp config/config_template.json config/config.json
```

2. Edit the configuration file and add your GitHub API token:
```json
{
  "github": {
    "api_token": "YOUR_GITHUB_PERSONAL_ACCESS_TOKEN",
    ...
  },
  ...
}
```

## Usage

### Displaying a user's activity summary
```bash
github-activities summary <username>
```

#### Options
- `--token`, `-t`: GitHub API token (overrides config file)
- `--config`, `-c`: Path to config file
- `--days`, `-d`: Number of days to look back for activity (default: 365)
- `--repository`, `-r`: Filter activity to a specific repository (format: 'owner/repo'). If not provided, all repositories will be included
- `--aggregation`, `-a`: Aggregate data by week or month (values: 'week' or 'month')

### Exporting activity data
```bash
github-activities export <username> --output data.json
```

#### Options
- `--token`, `-t`: GitHub API token (overrides config file)
- `--config`, `-c`: Path to config file
- `--days`, `-d`: Number of days to look back for activity (default: 365)
- `--output`, `-o`: Output file path (default: username_github_activity_YYYYMMDD.json or username_github_activity_YYYYMMDD.html)
- `--repository`, `-r`: Filter activity to a specific repository (format: 'owner/repo'). If not provided, all repositories will be included
- `--aggregation`, `-a`: Aggregate data by week or month (values: 'week' or 'month')
- `--format`, `-f`: Output format (values: 'json' or 'html', default: 'json')

## Examples

### Get activity summary for a user
```bash
github-activities summary octocat
```

### Get activity for the last 30 days
```bash
github-activities summary octocat --days 30
```

### Export activity data to a JSON file
```bash
github-activities export octocat --output octocat_activity.json
```

### Filter activity to a specific repository
```bash
github-activities summary octocat --repository octocat/Hello-World
```

### Aggregate activity by week
```bash
github-activities summary octocat --aggregation week
```

### Aggregate activity by month
```bash
github-activities summary octocat --aggregation month
```

### Export activity from a specific repository
```bash
github-activities export octocat --repository octocat/Hello-World --output octocat_hello_world.json
```

### Export activity with weekly aggregation
```bash
github-activities export octocat --aggregation week --output octocat_weekly.json
```

### Export activity with monthly aggregation
```bash
github-activities export octocat --aggregation month --output octocat_monthly.json
```

### Export activity as HTML with visualizations
```bash
github-activities export octocat --format html --output octocat_report.html
```

### Export activity as HTML with weekly aggregation for better visualizations
```bash
github-activities export octocat --format html --aggregation week --output octocat_weekly_report.html
```

## API Reference

If you want to use the GitHub Activities Tracker as a library in your own Python code, you can import the `GitHubClient` class:

```python
from github_activities.github_client import GitHubClient

# Initialize the client
client = GitHubClient(token="your_github_token")

# Get user activity summary
activity = client.get_user_activity_summary("octocat")

# Get user activity summary for a specific repository
activity = client.get_user_activity_summary("octocat", repository="octocat/Hello-World")

# Get user activity summary with weekly aggregation
activity = client.get_user_activity_summary("octocat", aggregation="week")

# Get user activity summary with monthly aggregation
activity = client.get_user_activity_summary("octocat", aggregation="month")

# Get specific activity types
commits = client.get_user_commits("octocat")
pull_requests = client.get_user_pull_requests("octocat")
issues = client.get_user_issues("octocat")
reviews = client.get_user_reviews("octocat")

# Filter by repository
commits = client.get_user_commits("octocat", repository="octocat/Hello-World")
pull_requests = client.get_user_pull_requests("octocat", repository="octocat/Hello-World")
issues = client.get_user_issues("octocat", repository="octocat/Hello-World")
reviews = client.get_user_reviews("octocat", repository="octocat/Hello-World")
```

## Troubleshooting

### Rate Limiting
GitHub API has rate limits. If you encounter rate limiting issues, try:
- Using a personal access token (increases rate limits)
- Reducing the date range with the `--days` option
- Enabling caching in the configuration file

### Authentication Errors
If you see authentication errors, check that:
- Your GitHub token is correct
- Your token has the necessary permissions
- Your token hasn't expired

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
