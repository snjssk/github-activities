import os
import json
from datetime import datetime
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
    <title>GitHub Contributions Comparison</title>
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
        }

        .header {
            background: white;
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            text-align: center;
        }

        .header h1 {
            font-size: 28px;
            margin-bottom: 8px;
            color: #2c3e50;
        }

        .header p {
            color: #6c757d;
            font-size: 16px;
        }

        .period-info {
            margin: 20px auto;
            text-align: center;
            padding: 12px 16px;
            background: #f8f9fa;
            border-radius: 6px;
            border-left: 4px solid #007bff;
            max-width: 400px;
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

        .users-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 32px;
        }

        .user-card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
        }

        .avatar {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            border: 3px solid #e9ecef;
            margin-bottom: 16px;
        }

        .user-name {
            font-size: 18px;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 8px;
        }

        .user-login {
            font-size: 14px;
            color: #6c757d;
            margin-bottom: 16px;
        }

        .user-stats {
            width: 100%;
            margin-top: 16px;
        }

        .stat-item {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #e9ecef;
        }

        .stat-item:last-child {
            border-bottom: none;
        }

        .stat-label {
            color: #6c757d;
        }

        .stat-value {
            font-weight: 600;
            color: #2c3e50;
        }

        .chart-section {
            background: white;
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 32px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }

        .chart-title {
            font-size: 20px;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 20px;
            padding-bottom: 8px;
            border-bottom: 1px solid #e9ecef;
            text-align: center;
        }

        .chart-container {
            position: relative;
            height: 400px;
            width: 100%;
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
        <!-- Header Section -->
        <div class="header">
            <h1>{% if jp_week_format %}GitHub 貢献比較{% else %}GitHub Contributions Comparison{% endif %}</h1>
            <p>{% if jp_week_format %}複数ユーザーの貢献活動を比較{% else %}Comparing contributions across multiple users{% endif %}</p>
        </div>

        <div class="period-info">
            <h3>{% if jp_week_format %}活動期間{% else %}Activity Period{% endif %}</h3>
            <p>{{ activity_period.since[:10] }} 〜 {{ activity_period.until[:10] }}</p>
        </div>

        <!-- Users Grid -->
        <div class="users-grid">
            {% for user_data in users_data %}
            <div class="user-card">
                <img src="{{ user_data.user.avatar_url }}" alt="{{ user_data.user.login }}" class="avatar">
                <div class="user-name">{{ user_data.user.name or user_data.user.login }}</div>
                <div class="user-login">@{{ user_data.user.login }}</div>
                <div class="user-stats">
                    <div class="stat-item">
                        <span class="stat-label">{% if jp_week_format %}総貢献数{% else %}Total Contributions{% endif %}</span>
                        <span class="stat-value">{{ user_data.summary.total_contributions }}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">{% if jp_week_format %}コミット{% else %}Commits{% endif %}</span>
                        <span class="stat-value">{{ user_data.summary.commits_count }}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">{% if jp_week_format %}プルリクエスト{% else %}Pull Requests{% endif %}</span>
                        <span class="stat-value">{{ user_data.summary.pull_requests_count }}</span>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>

        <!-- Total Contributions Chart -->
        <div class="chart-section">
            <h2 class="chart-title">{% if jp_week_format %}総貢献数の比較{% else %}Total Contributions Comparison{% endif %}</h2>
            <div class="chart-container">
                <canvas id="contributionsChart"></canvas>
            </div>
        </div>

        <div class="footer">
            <p>Generated by GitHub Activities Tracker on {{ generation_date }}</p>
        </div>
    </div>

    <script>
        // Data for charts
        const contributionsData = {
            labels: [{% for period in periods %}"{{ period }}"{% if not loop.last %}, {% endif %}{% endfor %}],
            datasets: [
                {% for user_data in users_data %}
                {
                    label: "{{ user_data.user.name or user_data.user.login }}",
                    data: [{% for period, count in user_data.aggregated.total_contributions %}{{ count }}{% if not loop.last %}, {% endif %}{% endfor %}],
                    borderColor: "{{ user_data.color }}",
                    backgroundColor: "{{ user_data.color }}20",
                    borderWidth: 3,
                    fill: false,
                    tension: 0.4,
                    pointBackgroundColor: "{{ user_data.color }}",
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 5
                }{% if not loop.last %},{% endif %}
                {% endfor %}
            ]
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
                        usePointStyle: true,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
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

        // Create the contributions chart
        const contributionsCtx = document.getElementById('contributionsChart').getContext('2d');
        new Chart(contributionsCtx, {
            type: 'line',
            data: contributionsData,
            options: chartOptions
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
        
        # Render the template
        template = jinja2.Template(self.template)
        html_content = template.render(
            users_data=users_data,
            activity_period=activity_period,
            periods=periods,
            jp_week_format=self.jp_week_format,
            generation_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # Save to file if output path is provided
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            return output_path
        
        return html_content