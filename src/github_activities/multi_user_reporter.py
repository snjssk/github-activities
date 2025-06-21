import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import jinja2

from github_activities.github_client import GitHubClient


class MultiUserReporter:
    """Class for generating HTML reports comparing multiple GitHub users."""

    def __init__(self, jp_week_format=False):
        """
        Initialize the multi-user reporter.

        Args:
            jp_week_format: Whether to use Japanese-style week notation (showing start date).
        """
        self.jp_week_format = jp_week_format
        self.is_japanese = jp_week_format  # Use jp_week_format as a proxy for Japanese language preference
        # Create Jinja2 environment with template
        self.template = """
<!DOCTYPE html>
<html lang="{% if jp_week_format %}ja{% else %}en{% endif %}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitHub Team Productivity Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #f8f9fa;
            color: #333;
            line-height: 1.6;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            box-sizing: border-box;
        }

        .header {
            background: white;
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .header h1 {
            font-size: 28px;
            color: #2c3e50;
            margin: 0;
        }

        .period-info {
            text-align: right;
            padding: 12px 16px;
            background: #f8f9fa;
            border-radius: 6px;
            border-left: 4px solid #007bff;
        }

        .period-info h3 {
            font-size: 14px;
            color: #6c757d;
            margin-bottom: 4px;
        }

        .period-info p {
            font-size: 16px;
            font-weight: 600;
            color: #2c3e50;
        }

        /* Team Overview Stats */
        .team-overview {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 24px;
        }

        .overview-card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            text-align: center;
        }

        .overview-title {
            font-size: 14px;
            color: #6c757d;
            margin-bottom: 8px;
        }

        .overview-value {
            font-size: 32px;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 4px;
        }

        .overview-subtitle {
            font-size: 12px;
            color: #868e96;
        }

        /* Performance Ranking */
        .ranking-section {
            background: white;
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            box-sizing: border-box;
        }

        .section-title {
            font-size: 20px;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 20px;
            padding-bottom: 8px;
            border-bottom: 1px solid #e9ecef;
        }

        .ranking-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
        }

        .ranking-card {
            border: 1px solid #e9ecef;
            border-radius: 8px;
            overflow: hidden;
        }

        .ranking-header {
            background: #f8f9fa;
            padding: 12px 16px;
            font-weight: 600;
            color: #495057;
            border-bottom: 1px solid #e9ecef;
        }

        .ranking-item {
            display: flex;
            align-items: center;
            padding: 12px 16px;
            border-bottom: 1px solid #f1f3f4;
        }

        .ranking-item:last-child {
            border-bottom: none;
        }

        .rank-number {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: 600;
            margin-right: 12px;
        }

        .rank-1 { background: #ffd700; color: #000; }
        .rank-2 { background: #c0c0c0; color: #000; }
        .rank-3 { background: #cd7f32; color: #fff; }
        .rank-other { background: #e9ecef; color: #6c757d; }

        .rank-avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            margin-right: 12px;
        }

        .rank-info {
            flex: 1;
        }

        .rank-name {
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 2px;
        }

        .rank-login {
            font-size: 12px;
            color: #6c757d;
        }

        .rank-value {
            font-weight: 700;
            color: #007bff;
            margin-left: auto;
        }

        /* Charts Grid */
        .charts-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 24px;
            margin-bottom: 24px;
        }

        .chart-card {
            background: white;
            border-radius: 8px;
            padding: 24px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }

        .chart-title {
            font-size: 18px;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 20px;
            padding-bottom: 8px;
            border-bottom: 1px solid #e9ecef;
        }

        .chart-container {
            position: relative;
            height: 400px;
            width: 100%;
        }

        /* Member Details Grid */
        .members-grid {
            display: flex;
            gap: 20px;
            margin-bottom: 24px;
            justify-content: center;
            flex-wrap: wrap;
        }

        .member-card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            position: relative;
            width: 280px;
            flex-shrink: 0;
        }

        .member-header {
            display: flex;
            align-items: center;
            margin-bottom: 16px;
        }

        .member-avatar {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            margin-right: 12px;
        }

        .member-info h3 {
            color: #2c3e50;
            margin-bottom: 2px;
        }

        .member-info p {
            color: #6c757d;
            font-size: 14px;
        }

        .performance-badge {
            position: absolute;
            top: 12px;
            right: 12px;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
        }

        .high-performer { background: #d4edda; color: #155724; }
        .avg-performer { background: #fff3cd; color: #856404; }

        .member-stats {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
        }

        .member-stat {
            text-align: center;
            padding: 8px;
            background: #f8f9fa;
            border-radius: 6px;
        }

        .member-stat-value {
            font-size: 20px;
            font-weight: 700;
            color: #2c3e50;
        }

        .member-stat-label {
            font-size: 12px;
            color: #6c757d;
            margin-top: 2px;
        }

        .footer {
            text-align: center;
            margin-top: 32px;
            color: #6c757d;
            font-size: 14px;
        }

        @media (max-width: 768px) {
            .users-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>📊 Team Productivity Dashboard</h1>
            <div class="period-info">
                <h3>{% if jp_week_format %}分析期間{% else %}Analysis Period{% endif %}</h3>
                <p>{{ activity_period_since_sliced }} 〜 {{ activity_period_until_sliced }}</p>
            </div>
        </div>

        <!-- Team Overview -->
        <div class="team-overview">
            <div class="overview-card">
                <div class="overview-title">Total Activity</div>
                <div class="overview-value">{{ total_activity }}</div>
                <div class="overview-subtitle">{% if jp_week_format %}アクティビティの合計{% else %}Sum of all activities{% endif %}</div>
            </div>
            <div class="overview-card">
                <div class="overview-title">Average Activity</div>
                <div class="overview-value">{{ average_activity|round|int }}</div>
                <div class="overview-subtitle">{% if jp_week_format %}メンバー1人あたりの平均{% else %}Average per member{% endif %}</div>
            </div>
            <div class="overview-card">
                <div class="overview-title">Total PR</div>
                <div class="overview-value">{{ total_pr }}</div>
                <div class="overview-subtitle">{% if jp_week_format %}Pull Requestの合計{% else %}Sum of all PRs{% endif %}</div>
            </div>
            <div class="overview-card">
                <div class="overview-title">Average PR</div>
                <div class="overview-value">{{ average_pr|round|int }}</div>
                <div class="overview-subtitle">{% if jp_week_format %}メンバー1人あたりの平均{% else %}Average per member{% endif %}</div>
            </div>
        </div>

        <!-- Performance Rankings -->
        <div class="ranking-section">
            <h2 class="section-title">🏆 Performance</h2>
            <div class="ranking-grid">
                <div class="ranking-card">
                    <div class="ranking-header">Total Activity</div>
                    {% for user_data in top_contributors %}
                    <div class="ranking-item">
                        <div class="rank-number rank-{{ loop.index }}">{{ loop.index }}</div>
                        <img src="{{ user_data.user.avatar_url }}" alt="{{ user_data.user.login }}" class="rank-avatar">
                        <div class="rank-info">
                            <div class="rank-name">{{ user_data.user.name or user_data.user.login }}</div>
                            <div class="rank-login">@{{ user_data.user.login }}</div>
                        </div>
                        <div class="rank-value">{{ user_data.summary.total_contributions }}</div>
                    </div>
                    {% endfor %}
                </div>

                <div class="ranking-card">
                    <div class="ranking-header">Daily Average Activity</div>
                    {% for user_data in top_daily_avg_activity %}
                    <div class="ranking-item">
                        <div class="rank-number rank-{{ loop.index }}">{{ loop.index }}</div>
                        <img src="{{ user_data.user.avatar_url }}" alt="{{ user_data.user.login }}" class="rank-avatar">
                        <div class="rank-info">
                            <div class="rank-name">{{ user_data.user.name or user_data.user.login }}</div>
                            <div class="rank-login">@{{ user_data.user.login }}</div>
                        </div>
                        <div class="rank-value">{{ user_data.daily_avg_activity|round(1) }}</div>
                    </div>
                    {% endfor %}
                </div>

                <div class="ranking-card">
                    <div class="ranking-header">Total PR</div>
                    {% for user_data in top_pr_contributors %}
                    <div class="ranking-item">
                        <div class="rank-number rank-{{ loop.index }}">{{ loop.index }}</div>
                        <img src="{{ user_data.user.avatar_url }}" alt="{{ user_data.user.login }}" class="rank-avatar">
                        <div class="rank-info">
                            <div class="rank-name">{{ user_data.user.name or user_data.user.login }}</div>
                            <div class="rank-login">@{{ user_data.user.login }}</div>
                        </div>
                        <div class="rank-value">{{ user_data.summary.pull_requests_count }}</div>
                    </div>
                    {% endfor %}
                </div>

                <div class="ranking-card">
                    <div class="ranking-header">Daily Average PR</div>
                    {% for user_data in top_daily_avg_pr %}
                    <div class="ranking-item">
                        <div class="rank-number rank-{{ loop.index }}">{{ loop.index }}</div>
                        <img src="{{ user_data.user.avatar_url }}" alt="{{ user_data.user.login }}" class="rank-avatar">
                        <div class="rank-info">
                            <div class="rank-name">{{ user_data.user.name or user_data.user.login }}</div>
                            <div class="rank-login">@{{ user_data.user.login }}</div>
                        </div>
                        <div class="rank-value">{{ user_data.daily_avg_pr|round(1) }}</div>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>

        <!-- Main Charts -->
        <div class="charts-grid">
            <div class="chart-card">
                <h3 class="chart-title">📈 Trends in Activity</h3>
                <div class="chart-container">
                    <canvas id="productivityChart"></canvas>
                </div>
            </div>

            <div class="chart-card">
                <h3 class="chart-title">🔄 Percentage of Activity</h3>
                <div class="chart-container">
                    <canvas id="contributionPieChart"></canvas>
                </div>
            </div>
        </div>

        <!-- Member Details -->
        <div class="ranking-section">
            <h2 class="section-title">👥 Member Details</h2>
            <div class="members-grid">
                {% for user_data in users_data %}
                <div class="member-card">
                    <div class="performance-badge {% if user_data.performance_label == 'High Performer' %}high-performer{% else %}avg-performer{% endif %}">
                        {{ user_data.performance_label }}
                    </div>
                    <div class="member-header">
                        <img src="{{ user_data.user.avatar_url }}" alt="{{ user_data.user.login }}" class="member-avatar">
                        <div class="member-info">
                            <h3>{{ user_data.user.name or user_data.user.login }}</h3>
                            <p>@{{ user_data.user.login }}</p>
                        </div>
                    </div>
                    <div class="member-stats">
                        <div class="member-stat">
                            <div class="member-stat-value">{{ user_data.summary.total_contributions }}</div>
                            <div class="member-stat-label">Activity</div>
                        </div>
                        <div class="member-stat">
                            <div class="member-stat-value">{{ user_data.daily_avg_activity|round(1) }}</div>
                            <div class="member-stat-label">Daily Average</div>
                        </div>
                        <div class="member-stat">
                            <div class="member-stat-value">{{ user_data.summary.pull_requests_count }}</div>
                            <div class="member-stat-label">Pull Request</div>
                        </div>
                        <div class="member-stat">
                            <div class="member-stat-value">{{ user_data.daily_avg_pr|round(1) }}</div>
                            <div class="member-stat-label">Daily Average</div>
                        </div>
                        <div class="member-stat">
                            <div class="member-stat-value">{{ user_data.summary.commits_count }}</div>
                            <div class="member-stat-label">Commits</div>
                        </div>
                        <div class="member-stat">
                            <div class="member-stat-value">{{ user_data.daily_avg_commits|round(1) }}</div>
                            <div class="member-stat-label">Daily Average</div>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>

        <div class="footer">
            <p>Generated by GitHub Team Productivity Tracker on {{ generation_date }}</p>
        </div>
    </div>

    <script>
        // Productivity trend data
        const productivityData = {
            labels: {{ periods_json|safe }},
            datasets: {{ datasets_json|safe }}
        };

        // Chart options
        const chartOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0,0,0,0.05)'
                    },
                    ticks: {
                        color: '#6c757d'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(0,0,0,0.05)'
                    },
                    ticks: {
                        color: '#6c757d'
                    }
                }
            }
        };

        // Create productivity chart
        const productivityCtx = document.getElementById('productivityChart').getContext('2d');
        new Chart(productivityCtx, {
            type: 'line',
            data: productivityData,
            options: chartOptions
        });

        // Contribution pie chart
        const pieCtx = document.getElementById('contributionPieChart').getContext('2d');
        new Chart(pieCtx, {
            type: 'doughnut',
            data: {
                labels: {{ user_labels_json|safe }},
                datasets: [{
                    data: {{ contribution_values_json|safe }},
                    backgroundColor: {{ user_colors_json|safe }},
                    borderWidth: 0,
                    cutout: '60%'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                }
            }
        });
    </script>
</body>
</html>
"""

    def generate_html_report(self, users_data: List[Dict], output_path: Optional[str] = None) -> str:
        """
        Generate an HTML report comparing multiple users' contributions.

        Args:
            users_data: List of dictionaries with user activity data
            output_path: Path where the HTML report will be saved

        Returns:
            Path to the generated HTML report
        """
        # Ensure all users have the same activity period
        activity_period = users_data[0]["activity_period"]

        # Pre-compute sliced values for activity period
        activity_period_since_sliced = activity_period["since"][:10] if "since" in activity_period else ""
        activity_period_until_sliced = activity_period["until"][:10] if "until" in activity_period else ""

        # Assign colors to users
        colors = ["#007bff", "#28a745", "#ffc107", "#dc3545", "#6610f2", "#fd7e14", "#20c997", "#e83e8c"]
        for i, user_data in enumerate(users_data):
            user_data["color"] = colors[i % len(colors)]

        # Get all unique periods from all users
        all_periods = set()
        for user_data in users_data:
            if "aggregated" in user_data and "total_contributions" in user_data["aggregated"]:
                for period, _ in user_data["aggregated"]["total_contributions"]:
                    all_periods.add(period)

        # Sort periods
        periods = sorted(list(all_periods))

        # Calculate additional metrics
        total_activity = sum(user_data["summary"]["total_contributions"] for user_data in users_data)
        average_activity = total_activity / len(users_data) if users_data else 0
        total_pr = sum(user_data["summary"]["pull_requests_count"] for user_data in users_data)
        average_pr = total_pr / len(users_data) if users_data else 0

        # Calculate daily averages and performance labels for each user
        days_in_period = activity_period["days"]
        for user_data in users_data:
            # Daily averages
            user_data["daily_avg_activity"] = user_data["summary"]["total_contributions"] / days_in_period if days_in_period else 0
            user_data["daily_avg_pr"] = user_data["summary"]["pull_requests_count"] / days_in_period if days_in_period else 0
            user_data["daily_avg_commits"] = user_data["summary"]["commits_count"] / days_in_period if days_in_period else 0

            # Activity percentage
            user_data["activity_percentage"] = (user_data["summary"]["total_contributions"] / total_activity * 100) if total_activity else 0

            # Performance label
            user_data["performance_label"] = "High Performer" if user_data["summary"]["total_contributions"] > average_activity else "Average"

            # Extract contribution values for the chart
            if "aggregated" in user_data and "total_contributions" in user_data["aggregated"]:
                # Create a dictionary to map periods to their counts
                contributions_dict = {period: count for period, count in user_data["aggregated"]["total_contributions"]}

                # Create a list of counts in the same order as the periods list
                user_data["aggregated"]["total_contributions_values"] = [
                    contributions_dict.get(period, 0) for period in periods
                ]

        # Prepare data for pie chart
        user_labels = [user_data["user"]["name"] or user_data["user"]["login"] for user_data in users_data]
        contribution_values = [user_data["summary"]["total_contributions"] for user_data in users_data]
        user_colors = [user_data["color"] for user_data in users_data]

        # Convert to JSON strings
        user_labels_json = json.dumps(user_labels)
        contribution_values_json = json.dumps(contribution_values)
        user_colors_json = json.dumps(user_colors)

        # Prepare data for ranking cards
        top_contributors = sorted(users_data, key=lambda x: x["summary"]["total_contributions"], reverse=True)[:2]
        top_daily_avg_activity = sorted(users_data, key=lambda x: x["daily_avg_activity"], reverse=True)[:2]
        top_pr_contributors = sorted(users_data, key=lambda x: x["summary"]["pull_requests_count"], reverse=True)[:2]
        top_daily_avg_pr = sorted(users_data, key=lambda x: x["daily_avg_pr"], reverse=True)[:2]

        # Prepare data for productivity chart
        periods_json = json.dumps([period for period in periods])
        datasets = []
        for user_data in users_data:
            if "aggregated" in user_data and "total_contributions_values" in user_data["aggregated"]:
                dataset = {
                    "label": user_data["user"]["name"] or user_data["user"]["login"],
                    "data": user_data["aggregated"]["total_contributions_values"],
                    "borderColor": user_data["color"],
                    "backgroundColor": user_data["color"] + "20",
                    "borderWidth": 3,
                    "fill": True,
                    "tension": 0.4,
                    "pointBackgroundColor": user_data["color"],
                    "pointBorderColor": "#fff",
                    "pointBorderWidth": 2,
                    "pointRadius": 6
                }
                datasets.append(dataset)
        datasets_json = json.dumps(datasets)

        # Render the template
        template = jinja2.Template(self.template)
        html_content = template.render(
            users_data=users_data,
            activity_period=activity_period,
            activity_period_since_sliced=activity_period_since_sliced,
            activity_period_until_sliced=activity_period_until_sliced,
            periods=periods,
            jp_week_format=self.jp_week_format,
            generation_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            total_activity=total_activity,
            average_activity=average_activity,
            total_pr=total_pr,
            average_pr=average_pr,
            user_labels=user_labels,
            contribution_values=contribution_values,
            user_colors=user_colors,
            user_labels_json=user_labels_json,
            contribution_values_json=contribution_values_json,
            user_colors_json=user_colors_json,
            periods_json=periods_json,
            datasets_json=datasets_json,
            top_contributors=top_contributors,
            top_daily_avg_activity=top_daily_avg_activity,
            top_pr_contributors=top_pr_contributors,
            top_daily_avg_pr=top_daily_avg_pr
        )

        # Save to file if output path is provided
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            return output_path

        return html_content
