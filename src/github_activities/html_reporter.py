"""
HTML Report Generator

This module provides functionality to generate HTML reports with interactive
charts for GitHub activity data.
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import jinja2
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder


class HTMLReporter:
    """Class for generating HTML reports with interactive charts."""

    def __init__(self, jp_week_format=False):
        """
        Initialize the HTML reporter.

        Args:
            jp_week_format: Whether to use Japanese-style week notation (showing start date).
        """
        self.jp_week_format = jp_week_format
        # Create Jinja2 environment with template
        self.template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitHub Activity Report for {{ user.login }}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            color: #333;
            background-color: #f8f9fa;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .header {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
            border-bottom: 1px solid #eee;
            padding-bottom: 20px;
        }
        .avatar {
            width: 100px;
            height: 100px;
            border-radius: 50%;
            margin-right: 20px;
        }
        .user-info {
            flex-grow: 1;
        }
        .user-info h1 {
            margin: 0 0 10px 0;
        }
        .user-info p {
            margin: 5px 0;
            color: #666;
        }
        .summary-box {
            display: flex;
            flex-wrap: wrap;
            margin-bottom: 30px;
        }
        .summary-item {
            flex: 1;
            min-width: 150px;
            background-color: #f8f9fa;
            border-radius: 5px;
            padding: 15px;
            margin: 5px;
            text-align: center;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .summary-item h3 {
            margin: 0 0 10px 0;
            color: #555;
        }
        .summary-item p {
            font-size: 24px;
            font-weight: bold;
            margin: 0;
            color: #007bff;
        }
        .chart-container {
            margin-bottom: 30px;
            background-color: white;
            border-radius: 5px;
            padding: 15px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .chart-title {
            margin-top: 0;
            color: #333;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #777;
            font-size: 14px;
        }
        @media (max-width: 768px) {
            .summary-box {
                flex-direction: column;
            }
            .summary-item {
                margin-bottom: 10px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="{{ user.avatar_url }}" alt="{{ user.login }}" class="avatar">
            <div class="user-info">
                <h1>{{ user.name or user.login }}</h1>
                <p>GitHub Username: <a href="{{ user.html_url }}" target="_blank">{{ user.login }}</a></p>
                <p>Public Repositories: {{ user.public_repos }}</p>
                <p>Followers: {{ user.followers }} | Following: {{ user.following }}</p>
                <p>Account Created: {{ user.created_at[:10] }}</p>
            </div>
        </div>

        <h2>Activity Summary ({{ activity_period.since[:10] }} to {{ activity_period.until[:10] }})</h2>

        <div class="summary-box">
            <div class="summary-item">
                <h3>Commits</h3>
                <p>{{ summary.commits_count }}</p>
            </div>
            <div class="summary-item">
                <h3>Pull Requests</h3>
                <p>{{ summary.pull_requests_count }}</p>
            </div>
            <div class="summary-item">
                <h3>Issues</h3>
                <p>{{ summary.issues_count }}</p>
            </div>
            <div class="summary-item">
                <h3>Reviews</h3>
                <p>{{ summary.reviews_count }}</p>
            </div>
            <div class="summary-item">
                <h3>Total Contributions</h3>
                <p>{{ summary.total_contributions }}</p>
            </div>
        </div>

        {% if aggregated %}
        <h2>Activity Trends</h2>

        {% if aggregated.commits %}
        <div class="chart-container">
            <h3 class="chart-title">Commits Over Time</h3>
            <div id="commits-chart"></div>
        </div>
        {% endif %}

        {% if aggregated.pull_requests %}
        <div class="chart-container">
            <h3 class="chart-title">Pull Requests Over Time</h3>
            <div id="prs-chart"></div>
        </div>
        {% endif %}

        {% if aggregated.issues %}
        <div class="chart-container">
            <h3 class="chart-title">Issues Over Time</h3>
            <div id="issues-chart"></div>
        </div>
        {% endif %}

        {% if aggregated.reviews %}
        <div class="chart-container">
            <h3 class="chart-title">Reviews Over Time</h3>
            <div id="reviews-chart"></div>
        </div>
        {% endif %}
        {% endif %}

        <div class="footer">
            <p>Generated by GitHub Activities Tracker on {{ generation_date }}</p>
        </div>
    </div>

    {% if aggregated %}
    <script>
        // Plotly chart data
        var plotlyData = {{ plotly_data|safe }};

        {% if aggregated.commits %}
        Plotly.newPlot('commits-chart', plotlyData.commits.data, plotlyData.commits.layout);
        {% endif %}

        {% if aggregated.pull_requests %}
        Plotly.newPlot('prs-chart', plotlyData.pull_requests.data, plotlyData.pull_requests.layout);
        {% endif %}

        {% if aggregated.issues %}
        Plotly.newPlot('issues-chart', plotlyData.issues.data, plotlyData.issues.layout);
        {% endif %}

        {% if aggregated.reviews %}
        Plotly.newPlot('reviews-chart', plotlyData.reviews.data, plotlyData.reviews.layout);
        {% endif %}
    </script>
    {% endif %}
</body>
</html>
"""

    def _convert_week_to_jp_format(self, week_str):
        """
        Convert week string (e.g., '2023-W01') to Japanese-style notation (e.g., '2023-01-02').

        Args:
            week_str: Week string in format 'YYYY-WNN'

        Returns:
            String with the date of the first day of the week in format 'YYYY-MM-DD'
        """
        try:
            # Parse the year and week number
            year_str, week_part = week_str.split('-')
            year = int(year_str)
            week_num = int(week_part[1:])

            # Create a date object for the first day of the year
            first_day = datetime(year, 1, 1)

            # Calculate the first day of the week
            # The %W format considers the week to start on Monday and the first week of the year to be the first week with a Monday in it
            # So we need to adjust by adding the days from the start of the year to the first Monday, then adding (week_num - 1) * 7 days
            days_to_first_monday = (7 - first_day.weekday()) % 7
            days_to_add = days_to_first_monday + (week_num - 1) * 7
            week_start = first_day + timedelta(days=days_to_add)

            # Format the date as 'YYYY-MM-DD'
            return week_start.strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            # If there's any error, return the original string
            return week_str

    def _create_bar_chart_data(self, data, title):
        """
        Create Plotly bar chart data.

        Args:
            data: List of tuples with (period, count)
            title: Chart title

        Returns:
            Dictionary with Plotly chart data and layout
        """
        if not data:
            return None

        periods = []
        for item in data:
            period = item[0]
            # If jp_week_format is enabled and the period is a week, convert it to Japanese-style notation
            if self.jp_week_format and '-W' in period:
                period = self._convert_week_to_jp_format(period)
            periods.append(period)

        counts = [item[1] for item in data]

        chart_data = {
            'data': [
                go.Bar(
                    x=periods,
                    y=counts,
                    marker_color='#007bff'
                )
            ],
            'layout': go.Layout(
                title=title,
                xaxis=dict(title='Period'),
                yaxis=dict(title='Count'),
                margin=dict(l=50, r=50, t=50, b=50),
                height=400
            )
        }

        return chart_data

    def generate_html_report(self, user_data: Dict, output_path: Optional[str] = None) -> str:
        """
        Generate an HTML report with interactive charts.

        Args:
            user_data: Dictionary with user activity data
            output_path: Path where the HTML report will be saved

        Returns:
            Path to the generated HTML report
        """
        # Create Plotly chart data if aggregated data exists
        plotly_data = {}
        if "aggregated" in user_data:
            if user_data["aggregated"].get("commits"):
                plotly_data["commits"] = self._create_bar_chart_data(
                    user_data["aggregated"]["commits"], 
                    "Commits Over Time"
                )

            if user_data["aggregated"].get("pull_requests"):
                plotly_data["pull_requests"] = self._create_bar_chart_data(
                    user_data["aggregated"]["pull_requests"], 
                    "Pull Requests Over Time"
                )

            if user_data["aggregated"].get("issues"):
                plotly_data["issues"] = self._create_bar_chart_data(
                    user_data["aggregated"]["issues"], 
                    "Issues Over Time"
                )

            if user_data["aggregated"].get("reviews"):
                plotly_data["reviews"] = self._create_bar_chart_data(
                    user_data["aggregated"]["reviews"], 
                    "Reviews Over Time"
                )

        # Render the template
        template = jinja2.Template(self.template)
        html_content = template.render(
            user=user_data["user"],
            activity_period=user_data["activity_period"],
            summary=user_data["summary"],
            aggregated=user_data.get("aggregated", {}),
            plotly_data=json.dumps(plotly_data, cls=PlotlyJSONEncoder),
            generation_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        # Save to file if output path is provided
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            return output_path

        return html_content
