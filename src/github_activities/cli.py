"""
Command Line Interface for GitHub Activities Tracker

This module provides a CLI for interacting with the GitHub API
and displaying user activity data.
"""

import json
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import List, Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from github_activities.github_client import GitHubClient
from github_activities.html_reporter import HTMLReporter
from github_activities.multi_user_reporter import MultiUserReporter

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

console = Console()


def display_user_info(user_data):
    """Display user information in a rich panel."""
    user = user_data["user"]

    user_text = Text()
    user_text.append(f"Name: {user['name'] or 'N/A'}\n", style="bold")
    user_text.append(f"Username: {user['login']}\n")
    user_text.append(f"Profile: {user['html_url']}\n")
    user_text.append(f"Public Repos: {user['public_repos']}\n")
    user_text.append(f"Followers: {user['followers']}\n")
    user_text.append(f"Following: {user['following']}\n")
    user_text.append(f"Account Created: {user['created_at'][:10]}\n")

    console.print(Panel(user_text, title="User Information", expand=False))


def display_activity_summary(user_data):
    """Display activity summary in a rich table."""
    summary = user_data["summary"]
    period = user_data["activity_period"]

    table = Table(title=f"Activity Summary ({period['since'][:10]} to {period['until'][:10]})")

    table.add_column("Metric", style="cyan")
    table.add_column("Count", style="green")

    table.add_row("Commits", str(summary["commits_count"]))
    table.add_row("Pull Requests", str(summary["pull_requests_count"]))
    table.add_row("Issues", str(summary["issues_count"]))
    table.add_row("Reviews", str(summary["reviews_count"]))
    table.add_row("Total Contributions", str(summary["total_contributions"]))

    # Add code changes if available
    if "code_changes" in summary:
        code_changes = summary["code_changes"]
        table.add_row("Code Additions", str(code_changes["additions"]))
        table.add_row("Code Deletions", str(code_changes["deletions"]))
        table.add_row("Total Code Changes", str(code_changes["total"]))

    console.print(table)


def display_aggregated_activity(user_data, aggregation):
    """Display activity data aggregated by week or month."""
    aggregated = user_data["aggregated"]
    period_name = "Week" if aggregation == "week" else "Month"

    # Display aggregated commits
    if aggregated["commits"]:
        commit_table = Table(title=f"Commits by {period_name}")
        commit_table.add_column(period_name, style="cyan")
        commit_table.add_column("Count", style="green")

        for period, count in aggregated["commits"]:
            commit_table.add_row(period, str(count))

        console.print(commit_table)

    # Display aggregated pull requests
    if aggregated["pull_requests"]:
        pr_table = Table(title=f"Pull Requests by {period_name}")
        pr_table.add_column(period_name, style="cyan")
        pr_table.add_column("Count", style="green")

        for period, count in aggregated["pull_requests"]:
            pr_table.add_row(period, str(count))

        console.print(pr_table)

    # Display aggregated issues
    if aggregated["issues"]:
        issue_table = Table(title=f"Issues by {period_name}")
        issue_table.add_column(period_name, style="cyan")
        issue_table.add_column("Count", style="green")

        for period, count in aggregated["issues"]:
            issue_table.add_row(period, str(count))

        console.print(issue_table)

    # Display aggregated reviews
    if aggregated["reviews"]:
        review_table = Table(title=f"Reviews by {period_name}")
        review_table.add_column(period_name, style="cyan")
        review_table.add_column("Count", style="green")

        for period, count in aggregated["reviews"]:
            review_table.add_row(period, str(count))

        console.print(review_table)

    # Display aggregated code changes
    if "code_changes" in aggregated and aggregated["code_changes"]:
        code_changes_table = Table(title=f"Code Changes by {period_name}")
        code_changes_table.add_column(period_name, style="cyan")
        code_changes_table.add_column("Changes", style="green")

        for period, count in aggregated["code_changes"]:
            code_changes_table.add_row(period, str(count))

        console.print(code_changes_table)


def display_recent_activity(user_data):
    """Display recent activity details."""
    details = user_data["details"]

    # Display recent commits
    if details["commits"]:
        commit_table = Table(title="Recent Commits")
        commit_table.add_column("Date", style="cyan")
        commit_table.add_column("Repository", style="green")
        commit_table.add_column("Message", style="white")

        for commit in details["commits"]:
            commit_table.add_row(
                commit["date"][:10],
                commit["repository"],
                commit["message"].split("\n")[0][:50]  # First line, truncated
            )

        console.print(commit_table)

    # Display recent PRs
    if details["pull_requests"]:
        pr_table = Table(title="Recent Pull Requests")
        pr_table.add_column("Date", style="cyan")
        pr_table.add_column("Repository", style="green")
        pr_table.add_column("Title", style="white")
        pr_table.add_column("State", style="yellow")

        for pr in details["pull_requests"]:
            pr_table.add_row(
                pr["created_at"][:10],
                pr["repository"],
                pr["title"][:50],
                pr["state"]
            )

        console.print(pr_table)

    # Display recent issues
    if details["issues"]:
        issue_table = Table(title="Recent Issues")
        issue_table.add_column("Date", style="cyan")
        issue_table.add_column("Repository", style="green")
        issue_table.add_column("Title", style="white")
        issue_table.add_column("State", style="yellow")

        for issue in details["issues"]:
            issue_table.add_row(
                issue["created_at"][:10],
                issue["repository"],
                issue["title"][:50],
                issue["state"]
            )

        console.print(issue_table)


@click.group()
def cli():
    """GitHub Activities Tracker - Analyze GitHub user activities."""
    pass


@cli.command()
@click.argument("username", required=True)
@click.option(
    "--token", "-t", 
    help="GitHub API token. If not provided, will look for it in config file."
)
@click.option(
    "--config", "-c",
    help="Path to config file. Default is 'config/config.json'."
)
@click.option(
    "--days", "-d", 
    type=int, 
    default=365,
    help="Number of days to look back for activity. Default is 365."
)
@click.option(
    "--repository", "-r",
    help="Repository name to filter by (e.g., 'owner/repo'). If not provided, all repositories will be included."
)
@click.option(
    "--aggregation", "-a",
    type=click.Choice(["week", "month"]),
    help="Aggregate data by week or month."
)
@click.option(
    "--jp-week-format", "-j",
    is_flag=True,
    help="Use Japanese-style week notation (showing start date) instead of W01 format."
)
def summary(username, token, config, days, repository, aggregation, jp_week_format):
    """Display a summary of GitHub activities for a user."""
    try:
        # Initialize the GitHub client
        client = GitHubClient(token=token, config_path=config)

        # Calculate date range
        until = datetime.now()
        since = until - timedelta(days=days)

        # Get user activity data
        console.print(f"Fetching GitHub activity for [bold]{username}[/bold]...")
        if repository:
            console.print(f"Filtering by repository: [bold]{repository}[/bold]")
        if aggregation:
            console.print(f"Aggregating data by: [bold]{aggregation}[/bold]")
        user_data = client.get_user_activity_summary(username, since, until, repository, aggregation)

        # Display the data
        console.print()
        display_user_info(user_data)
        console.print()
        display_activity_summary(user_data)
        console.print()

        # Display aggregated data if requested
        if aggregation and "aggregated" in user_data:
            # If jp_week_format is enabled, convert week numbers to Japanese-style notation
            if jp_week_format and aggregation == "week":
                for activity_type in user_data["aggregated"]:
                    if user_data["aggregated"][activity_type]:
                        # Create a temporary HTMLReporter to use its conversion method
                        reporter = HTMLReporter(jp_week_format=True)
                        for i, (period, count) in enumerate(user_data["aggregated"][activity_type]):
                            if "-W" in period:
                                jp_period = reporter._convert_week_to_jp_format(period)
                                user_data["aggregated"][activity_type][i] = (jp_period, count)

            display_aggregated_activity(user_data, aggregation)
            console.print()

        display_recent_activity(user_data)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logger.error(f"Error in summary command: {e}", exc_info=True)
        sys.exit(1)


@cli.command()
@click.argument("username", required=True)
@click.option(
    "--token", "-t", 
    help="GitHub API token. If not provided, will look for it in config file."
)
@click.option(
    "--config", "-c",
    help="Path to config file. Default is 'config/config.json'."
)
@click.option(
    "--days", "-d", 
    type=int, 
    default=365,
    help="Number of days to look back for activity. Default is 365."
)
@click.option(
    "--output", "-o",
    help="Output file path for data."
)
@click.option(
    "--repository", "-r",
    help="Repository name to filter by (e.g., 'owner/repo'). If not provided, all repositories will be included."
)
@click.option(
    "--aggregation", "-a",
    type=click.Choice(["week", "month"]),
    help="Aggregate data by week or month."
)
@click.option(
    "--format", "-f",
    type=click.Choice(["json", "html"]),
    default="json",
    help="Output format (json or html). Default is json."
)
@click.option(
    "--jp-week-format", "-j",
    is_flag=True,
    help="Use Japanese-style week notation (showing start date) instead of W01 format."
)
def export(username, token, config, days, output, repository, aggregation, format, jp_week_format):
    """Export GitHub activities data as JSON or HTML."""
    try:
        # Initialize the GitHub client
        client = GitHubClient(token=token, config_path=config)

        # Calculate date range
        until = datetime.now()
        since = until - timedelta(days=days)

        # Get user activity data
        console.print(f"Fetching GitHub activity for [bold]{username}[/bold]...")
        if repository:
            console.print(f"Filtering by repository: [bold]{repository}[/bold]")
        if aggregation:
            console.print(f"Aggregating data by: [bold]{aggregation}[/bold]")
        user_data = client.get_user_activity_summary(username, since, until, repository, aggregation)

        # Determine output path and format
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if format == "json":
            # JSON output
            if not output:
                output = f"{username}_github_activity_{timestamp}.json"

            # Write to JSON file
            with open(output, "w") as f:
                json.dump(user_data, f, indent=2)

            console.print(f"Data exported to [bold]{output}[/bold] in JSON format")

        elif format == "html":
            # HTML output
            # Ensure aggregation is specified for HTML output
            if not aggregation:
                console.print("[yellow]Warning:[/yellow] No aggregation specified. Using 'week' as default for better visualizations.")
                aggregation = "week"
                # Re-fetch data with aggregation
                user_data = client.get_user_activity_summary(username, since, until, repository, aggregation)

            # Create reports directory if it doesn't exist
            reports_dir = "reports"
            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir)

            # Generate filename with aggregation type and timestamp
            if not output:
                output = os.path.join(reports_dir, f"{username}_github_activity_{aggregation}_{timestamp}.html")
            elif not os.path.isabs(output):
                # If output is not an absolute path, put it in the reports directory
                output = os.path.join(reports_dir, output)

            # Initialize HTML reporter and generate report
            reporter = HTMLReporter(jp_week_format=jp_week_format)
            html_path = reporter.generate_html_report(user_data, output)

            console.print(f"Report exported to [bold]{html_path}[/bold] in HTML format")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logger.error(f"Error in export command: {e}", exc_info=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--token", "-t", 
    help="GitHub API token to use."
)
@click.option(
    "--config", "-c",
    default="config/config.json",
    help="Path where config file will be created. Default is 'config/config.json'."
)
def setup(token, config):
    """Set up configuration for GitHub Activities Tracker."""
    try:
        # Check if config directory exists
        config_dir = os.path.dirname(config)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        # Check if config file already exists
        if os.path.exists(config):
            overwrite = click.confirm(f"Config file already exists at {config}. Overwrite?", default=False)
            if not overwrite:
                console.print("Setup cancelled.")
                return

        # Get token if not provided
        if not token:
            token = click.prompt("Enter your GitHub API token", hide_input=True)

        # Create config
        config_data = {
            "github": {
                "api_token": token,
                "api_url": "https://api.github.com",
                "user_agent": "GitHub-Activities-Tracker"
            },
            "app": {
                "default_username": "",
                "date_range": {
                    "start_date": (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
                    "end_date": datetime.now().strftime("%Y-%m-%d")
                },
                "metrics": {
                    "commits": True,
                    "pull_requests": True,
                    "issues": True,
                    "reviews": True,
                    "comments": True,
                    "stars": True
                },
                "cache": {
                    "enabled": True,
                    "expiry_hours": 24
                }
            },
            "display": {
                "theme": "dark",
                "chart_type": "bar",
                "output_format": "terminal"
            }
        }

        # Write config
        with open(config, "w") as f:
            json.dump(config_data, f, indent=2)

        console.print(f"Configuration saved to [bold]{config}[/bold]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logger.error(f"Error in setup command: {e}", exc_info=True)
        sys.exit(1)


@cli.command()
@click.argument("usernames", nargs=-1, required=True)
@click.option(
    "--token", "-t", 
    help="GitHub API token. If not provided, will look for it in config file."
)
@click.option(
    "--config", "-c",
    help="Path to config file. Default is 'config/config.json'."
)
@click.option(
    "--days", "-d", 
    type=int, 
    default=365,
    help="Number of days to look back for activity. Default is 365."
)
@click.option(
    "--output", "-o",
    help="Output file path for the comparison report."
)
@click.option(
    "--aggregation", "-a",
    type=click.Choice(["week", "month"]),
    default="week",
    help="Aggregate data by week or month. Default is week."
)
@click.option(
    "--jp-week-format", "-j",
    is_flag=True,
    help="Use Japanese-style week notation (showing start date) instead of W01 format."
)
def compare(usernames, token, config, days, output, aggregation, jp_week_format):
    """Compare GitHub contributions across multiple users."""
    try:
        # Initialize the GitHub client
        client = GitHubClient(token=token, config_path=config)

        # Calculate date range
        until = datetime.now()
        since = until - timedelta(days=days)

        # Fetch data for each user
        console.print(f"Fetching GitHub activity for [bold]{len(usernames)}[/bold] users...")
        users_data = []

        for username in usernames:
            console.print(f"Processing user: [bold]{username}[/bold]")
            user_data = client.get_user_activity_summary(username, since, until, None, aggregation)
            users_data.append(user_data)

        # Create reports directory if it doesn't exist
        reports_dir = "reports"
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if not output:
            usernames_str = "_".join(usernames[:3])  # Use first 3 usernames in filename
            if len(usernames) > 3:
                usernames_str += "_and_others"
            output = os.path.join(reports_dir, f"comparison_{usernames_str}_{timestamp}.html")
        elif not os.path.isabs(output):
            # If output is not an absolute path, put it in the reports directory
            output = os.path.join(reports_dir, output)

        # Initialize multi-user reporter and generate report
        reporter = MultiUserReporter(jp_week_format=jp_week_format)
        html_path = reporter.generate_html_report(users_data, output)

        console.print(f"Comparison report exported to [bold]{html_path}[/bold]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logger.error(f"Error in compare command: {e}", exc_info=True)
        sys.exit(1)


def main():
    """Main entry point for the CLI."""
    try:
        cli()
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {str(e)}")
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
