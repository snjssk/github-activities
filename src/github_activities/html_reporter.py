"""
HTML Report Generator

This module provides functionality to generate HTML reports with interactive
charts for GitHub activity data.
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

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
        self.is_japanese = jp_week_format  # Use jp_week_format as a proxy for Japanese language preference
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
            {% if summary.code_changes %}
            <div class="summary-item">
                <h3>Code Changes</h3>
                <p>{{ summary.code_changes.total }}</p>
                <small>+{{ summary.code_changes.additions }} / -{{ summary.code_changes.deletions }}</small>
            </div>
            {% endif %}
        </div>

        {% if analysis %}
        <div class="analysis-section" style="margin-bottom: 30px; background-color: white; border-radius: 5px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            {% if jp_week_format %}
            <h2>活動分析</h2>
            <div class="analysis-content" style="margin-top: 15px;">
                <p><strong>{{ analysis.period }}</strong></p>
                <h3>コミット</h3>
                <p>{{ analysis.commits }}</p>
                <h3>プルリクエスト</h3>
                <p>{{ analysis.pull_requests }}</p>
            </div>
            {% else %}
            <h2>Activity Analysis</h2>
            <div class="analysis-content" style="margin-top: 15px;">
                <p><strong>{{ analysis.period }}</strong></p>
                <h3>Commits</h3>
                <p>{{ analysis.commits }}</p>
                <h3>Pull Requests</h3>
                <p>{{ analysis.pull_requests }}</p>
            </div>
            {% endif %}
        </div>
        {% endif %}

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

        {% if aggregated.code_changes %}
        <div class="chart-container">
            <h3 class="chart-title">Code Changes Over Time</h3>
            <div id="code-changes-chart"></div>
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

        {% if aggregated.code_changes %}
        Plotly.newPlot('code-changes-chart', plotlyData.code_changes.data, plotlyData.code_changes.layout);
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

    def _generate_activity_analysis(self, user_data):
        """
        Generate analysis text based on activity data.

        Args:
            user_data: Dictionary with user activity data

        Returns:
            Dictionary with analysis text for different aspects
        """
        analysis = {}

        # Get aggregated data
        aggregated = user_data.get("aggregated", {})
        commits = aggregated.get("commits", [])
        pull_requests = aggregated.get("pull_requests", [])

        # Get summary data
        summary = user_data.get("summary", {})
        commits_count = summary.get("commits_count", 0)
        prs_count = summary.get("pull_requests_count", 0)

        # Analyze commits
        commit_analysis = self._analyze_trend(commits, "commits")

        # Analyze pull requests
        pr_analysis = self._analyze_trend(pull_requests, "pull requests")

        # Generate overall analysis
        if self.is_japanese:
            # Japanese analysis text
            analysis["commits"] = f"コミット分析: 期間中に合計 {commits_count} 件のコミットがありました。{commit_analysis['ja']}"
            analysis["pull_requests"] = f"プルリクエスト分析: 期間中に合計 {prs_count} 件のプルリクエストがありました。{pr_analysis['ja']}"

            # Overall period analysis
            period_analysis = ""
            if commit_analysis['trend'] == "increasing" and pr_analysis['trend'] == "increasing":
                period_analysis = "コミットとプルリクエストの両方が増加傾向にあり、活発な開発活動が行われています。"
            elif commit_analysis['trend'] == "decreasing" and pr_analysis['trend'] == "decreasing":
                period_analysis = "コミットとプルリクエストの両方が減少傾向にあります。プロジェクトが安定期に入ったか、活動が低下している可能性があります。"
            elif commit_analysis['trend'] == "stable" and pr_analysis['trend'] == "stable":
                period_analysis = "コミットとプルリクエストの活動は安定しています。一定のペースで開発が継続されています。"
            else:
                period_analysis = "コミットとプルリクエストの活動にはばらつきがあります。プロジェクトの異なるフェーズや、特定のタスクへの集中が見られます。"

            analysis["period"] = period_analysis
        else:
            # English analysis text
            analysis["commits"] = f"Commit Analysis: A total of {commits_count} commits were made during this period. {commit_analysis['en']}"
            analysis["pull_requests"] = f"Pull Request Analysis: A total of {prs_count} pull requests were created during this period. {pr_analysis['en']}"

            # Overall period analysis
            period_analysis = ""
            if commit_analysis['trend'] == "increasing" and pr_analysis['trend'] == "increasing":
                period_analysis = "Both commits and pull requests show an increasing trend, indicating active development."
            elif commit_analysis['trend'] == "decreasing" and pr_analysis['trend'] == "decreasing":
                period_analysis = "Both commits and pull requests show a decreasing trend. This might indicate the project is stabilizing or activity is slowing down."
            elif commit_analysis['trend'] == "stable" and pr_analysis['trend'] == "stable":
                period_analysis = "Commit and pull request activity is stable, showing consistent development pace."
            else:
                period_analysis = "There is variability in commit and pull request activity, which might indicate different project phases or focus on specific tasks."

            analysis["period"] = period_analysis

        return analysis

    def _analyze_trend(self, data, activity_type):
        """
        Analyze trend in activity data.

        Args:
            data: List of tuples with (period, count)
            activity_type: Type of activity (e.g., "commits", "pull requests")

        Returns:
            Dictionary with trend analysis
        """
        if not data or len(data) < 2:
            return {
                'trend': "insufficient_data",
                'en': f"Not enough data to analyze {activity_type} trend.",
                'ja': f"{activity_type}のトレンドを分析するのに十分なデータがありません。"
            }

        # Extract counts and calculate trend
        counts = [item[1] for item in data]
        first_half = counts[:len(counts)//2]
        second_half = counts[len(counts)//2:]

        first_half_avg = sum(first_half) / len(first_half) if first_half else 0
        second_half_avg = sum(second_half) / len(second_half) if second_half else 0

        # Determine trend
        trend_threshold = 0.2  # 20% change threshold
        percent_change = (second_half_avg - first_half_avg) / first_half_avg if first_half_avg > 0 else 0

        if abs(percent_change) < trend_threshold:
            trend = "stable"
            en_text = f"The {activity_type} activity has been relatively stable throughout the period."
            ja_text = f"期間を通じて{activity_type}の活動は比較的安定しています。"
        elif percent_change > 0:
            trend = "increasing"
            en_text = f"There is an increasing trend in {activity_type}, with approximately {int(percent_change * 100)}% more activity in the latter half of the period."
            ja_text = f"{activity_type}は増加傾向にあり、期間の後半では約{int(percent_change * 100)}%活動が増加しています。"
        else:
            trend = "decreasing"
            en_text = f"There is a decreasing trend in {activity_type}, with approximately {int(abs(percent_change) * 100)}% less activity in the latter half of the period."
            ja_text = f"{activity_type}は減少傾向にあり、期間の後半では約{int(abs(percent_change) * 100)}%活動が減少しています。"

        # Check for peaks
        max_count = max(counts)
        max_index = counts.index(max_count)
        max_period = data[max_index][0]

        if max_count > second_half_avg * 1.5:
            en_text += f" There was a notable peak in {activity_type} during {max_period}."
            ja_text += f" {max_period}の期間中に{activity_type}の顕著なピークがありました。"

        return {
            'trend': trend,
            'en': en_text,
            'ja': ja_text
        }

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

            if user_data["aggregated"].get("code_changes"):
                plotly_data["code_changes"] = self._create_bar_chart_data(
                    user_data["aggregated"]["code_changes"], 
                    "Code Changes Over Time"
                )

        # Generate activity analysis if aggregated data exists
        analysis = None
        if "aggregated" in user_data:
            analysis = self._generate_activity_analysis(user_data)

        # Render the template
        template = jinja2.Template(self.template)
        html_content = template.render(
            user=user_data["user"],
            activity_period=user_data["activity_period"],
            summary=user_data["summary"],
            aggregated=user_data.get("aggregated", {}),
            analysis=analysis,
            jp_week_format=self.jp_week_format,
            plotly_data=json.dumps(plotly_data, cls=PlotlyJSONEncoder),
            generation_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        # Save to file if output path is provided
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            return output_path

        return html_content
