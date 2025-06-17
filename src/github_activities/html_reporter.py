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
<html lang="{% if jp_week_format %}ja{% else %}en{% endif %}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitHub Activity Dashboard - {{ user.login }}</title>
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
            display: flex;
            align-items: center;
            gap: 20px;
        }

        .avatar {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            border: 3px solid #e9ecef;
        }

        .user-info h1 {
            font-size: 28px;
            margin-bottom: 8px;
            color: #2c3e50;
        }

        .user-meta {
            display: flex;
            gap: 16px;
            font-size: 14px;
            color: #6c757d;
            flex-wrap: wrap;
        }

        .period-info {
            margin-left: auto;
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

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
            margin-bottom: 32px;
        }

        .stat-card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            transition: box-shadow 0.2s ease;
        }

        .stat-card:hover {
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
        }

        .stat-header {
            display: flex;
            justify-content: between;
            align-items: center;
            margin-bottom: 12px;
        }

        .stat-title {
            font-size: 14px;
            color: #6c757d;
            font-weight: 500;
        }

        .stat-value {
            font-size: 32px;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 4px;
        }

        .stat-subtitle {
            font-size: 12px;
            color: #868e96;
        }

        .analysis-section {
            background: white;
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 32px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }

        .analysis-section h2 {
            color: #2c3e50;
            margin-bottom: 16px;
            font-size: 20px;
        }

        .analysis-content p {
            margin-bottom: 12px;
            color: #495057;
        }

        .analysis-content h3 {
            color: #343a40;
            margin: 16px 0 8px 0;
            font-size: 16px;
        }

        .charts-section {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
            margin-bottom: 32px;
        }

        .chart-card {
            background: white;
            border-radius: 8px;
            padding: 24px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            width: 100%;
            overflow: hidden;
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
            height: 300px;
            width: 100%;
            overflow: hidden;
        }

        .trends-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
        }

        .trend-chart {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }

        .trend-chart h3 {
            font-size: 16px;
            color: #2c3e50;
            margin-bottom: 16px;
            padding-bottom: 8px;
            border-bottom: 1px solid #e9ecef;
        }

        .trend-chart-container {
            height: 250px;
        }

        .footer {
            text-align: center;
            margin-top: 32px;
            color: #6c757d;
            font-size: 14px;
        }

        @media (max-width: 768px) {
            .header {
                flex-direction: column;
                text-align: center;
            }

            .period-info {
                margin-left: 0;
                text-align: center;
            }

            .charts-section {
                grid-template-columns: 1fr;
            }

            .stats-grid {
                grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header Section -->
        <div class="header">
            <img src="{{ user.avatar_url }}" alt="{{ user.login }}" class="avatar">
            <div class="user-info">
                <h1>{{ user.name or user.login }}</h1>
                <div class="user-meta">
                    <span>📁 {{ user.public_repos }} repositories</span>
                    <span>👥 {{ user.followers }} followers</span>
                    <span>📅 Since {{ user.created_at[:7] }}</span>
                </div>
            </div>
            <div class="period-info">
                <h3>{% if jp_week_format %}Activity Period{% else %}Activity Period{% endif %}</h3>
                <p>{{ activity_period.since[:10] }} 〜 {{ activity_period.until[:10] }}</p>
            </div>
        </div>

        <!-- Stats Overview -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-title">Total Contributions</div>
                <div class="stat-value">{{ summary.total_contributions }}</div>
                <div class="stat-subtitle">{% if jp_week_format %}全活動の合計{% else %}Sum of all activities{% endif %}</div>
            </div>

            <div class="stat-card">
                <div class="stat-title">Total Commits</div>
                <div class="stat-value">{{ summary.commits_count }}</div>
                <div class="stat-subtitle">{% if jp_week_format %}過去30日間{% else %}Last 30 days{% endif %}</div>
            </div>

            <div class="stat-card">
                <div class="stat-title">Pull Requests</div>
                <div class="stat-value">{{ summary.pull_requests_count }}</div>
                <div class="stat-subtitle">{% if jp_week_format %}平均 {{ (summary.pull_requests_count / 4)|round(1) }}/週{% else %}Avg {{ (summary.pull_requests_count / 4)|round(1) }}/week{% endif %}</div>
            </div>

            {% if summary.code_changes %}
            <div class="stat-card">
                <div class="stat-title">Code Changes</div>
                <div class="stat-value">{{ (summary.code_changes.total / 1000)|round(1) }}k</div>
                <div class="stat-subtitle">+{{ (summary.code_changes.additions / 1000)|round(1) }}k / -{{ (summary.code_changes.deletions / 1000)|round(1) }}k</div>
            </div>
            {% endif %}

            <div class="stat-card">
                <div class="stat-title">Issues</div>
                <div class="stat-value">{{ summary.issues_count }}</div>
                <div class="stat-subtitle">{% if jp_week_format %}課題管理{% else %}Issue management{% endif %}</div>
            </div>

            <div class="stat-card">
                <div class="stat-title">Code Reviews</div>
                <div class="stat-value">{{ summary.reviews_count }}</div>
                <div class="stat-subtitle">{% if jp_week_format %}レビュー参加{% else %}Review participation{% endif %}</div>
            </div>
        </div>

        {% if analysis %}
        <div class="analysis-section">
            <h2>{% if jp_week_format %}活動分析{% else %}Activity Analysis{% endif %}</h2>
            <div class="analysis-content">
                <p><strong>{{ analysis.period }}</strong></p>
                {% if jp_week_format %}
                <h3>コミット</h3>
                <p>{{ analysis.commits }}</p>
                <h3>プルリクエスト</h3>
                <p>{{ analysis.pull_requests }}</p>
                {% else %}
                <h3>Commits</h3>
                <p>{{ analysis.commits }}</p>
                <h3>Pull Requests</h3>
                <p>{{ analysis.pull_requests }}</p>
                {% endif %}
            </div>
        </div>
        {% endif %}

        {% if aggregated %}
        <!-- Main Charts Section -->
        <div class="charts-section">
            <div class="chart-card">
                <h3 class="chart-title">{% if jp_week_format %}活動トレンド推移{% else %}Activity Trend{% endif %}</h3>
                <div class="chart-container">
                    <canvas id="trendChart"></canvas>
                </div>
            </div>

            <div class="chart-card">
                <h3 class="chart-title">{% if jp_week_format %}活動内訳{% else %}Activity Breakdown{% endif %}</h3>
                <div class="chart-container">
                    <canvas id="pieChart"></canvas>
                </div>
            </div>
        </div>

        <!-- Individual Trend Charts -->
        <div class="trends-grid">
            {% if aggregated.commits %}
            <div class="trend-chart">
                <h3>Commits</h3>
                <div class="trend-chart-container">
                    <canvas id="commitsChart"></canvas>
                </div>
            </div>
            {% endif %}

            {% if aggregated.pull_requests %}
            <div class="trend-chart">
                <h3>Pull Requests</h3>
                <div class="trend-chart-container">
                    <canvas id="prsChart"></canvas>
                </div>
            </div>
            {% endif %}

            {% if aggregated.code_changes %}
            <div class="trend-chart">
                <h3>Code Changes</h3>
                <div class="trend-chart-container">
                    <canvas id="codeChangesChart"></canvas>
                </div>
            </div>
            {% endif %}

            {% if aggregated.reviews %}
            <div class="trend-chart">
                <h3>Code Reviews</h3>
                <div class="trend-chart-container">
                    <canvas id="reviewsChart"></canvas>
                </div>
            </div>
            {% endif %}
        </div>
        {% endif %}

        <div class="footer">
            <p>Generated by GitHub Activities Tracker on {{ generation_date }}</p>
        </div>
    </div>

    {% if aggregated %}
    <script>
        // Data for charts
        const data = {
            periods: [{% for period in aggregated.total_contributions %}"{{ period[0] }}"{% if not loop.last %}, {% endif %}{% endfor %}],
            totalContributions: [{% for period in aggregated.total_contributions %}{{ period[1] }}{% if not loop.last %}, {% endif %}{% endfor %}],
            commits: [{% for period in aggregated.commits %}{{ period[1] }}{% if not loop.last %}, {% endif %}{% endfor %}],
            pullRequests: [{% for period in aggregated.pull_requests %}{{ period[1] }}{% if not loop.last %}, {% endif %}{% endfor %}],
            {% if aggregated.issues %}
            issues: [{% for period in aggregated.issues %}{{ period[1] }}{% if not loop.last %}, {% endif %}{% endfor %}],
            {% endif %}
            {% if aggregated.reviews %}
            reviews: [{% for period in aggregated.reviews %}{{ period[1] }}{% if not loop.last %}, {% endif %}{% endfor %}],
            {% endif %}
            {% if aggregated.code_changes %}
            codeChanges: [{% for period in aggregated.code_changes %}{{ period[1] }}{% if not loop.last %}, {% endif %}{% endfor %}]
            {% endif %}
        };

        // Common chart options
        const commonOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
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

        // Main trend chart
        const trendCtx = document.getElementById('trendChart').getContext('2d');
        new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: data.periods.map(p => p.slice(5)),
                datasets: [{
                    label: 'Total Contributions',
                    data: data.totalContributions,
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#007bff',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 5
                }]
            },
            options: {
                ...commonOptions,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                }
            }
        });

        // Activity breakdown pie chart
        const pieCtx = document.getElementById('pieChart').getContext('2d');
        new Chart(pieCtx, {
            type: 'doughnut',
            data: {
                labels: ['Commits', 'Pull Requests', 'Reviews', 'Issues'],
                datasets: [{
                    data: [{{ summary.commits_count }}, {{ summary.pull_requests_count }}, {{ summary.reviews_count }}, {{ summary.issues_count }}],
                    backgroundColor: [
                        '#007bff',
                        '#28a745',
                        '#ffc107',
                        '#dc3545'
                    ],
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
                            usePointStyle: true,
                            font: {
                                size: 12
                            }
                        }
                    }
                }
            }
        });

        // Individual trend charts
        function createTrendChart(canvasId, chartData, color, label) {
            const ctx = document.getElementById(canvasId).getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.periods.map(p => p.slice(5)),
                    datasets: [{
                        label: label,
                        data: chartData,
                        backgroundColor: color,
                        borderRadius: 4
                    }]
                },
                options: commonOptions
            });
        }

        // Create individual charts
        {% if aggregated.commits %}
        createTrendChart('commitsChart', data.commits, '#007bff', 'Commits');
        {% endif %}
        {% if aggregated.pull_requests %}
        createTrendChart('prsChart', data.pullRequests, '#28a745', 'Pull Requests');
        {% endif %}
        {% if aggregated.reviews %}
        createTrendChart('reviewsChart', data.reviews, '#ffc107', 'Reviews');
        {% endif %}
        {% if aggregated.code_changes %}
        createTrendChart('codeChangesChart', data.codeChanges, '#dc3545', 'Code Changes');
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
        total_contributions = aggregated.get("total_contributions", [])

        # Get summary data
        summary = user_data.get("summary", {})
        commits_count = summary.get("commits_count", 0)
        prs_count = summary.get("pull_requests_count", 0)
        total_contributions_count = summary.get("total_contributions", 0)

        # Analyze commits
        commit_analysis = self._analyze_trend(commits, "commits")

        # Analyze pull requests
        pr_analysis = self._analyze_trend(pull_requests, "pull requests")

        # Analyze total contributions
        total_contributions_analysis = self._analyze_trend(total_contributions, "total contributions")

        # Generate overall analysis
        if self.is_japanese:
            # Japanese analysis text
            analysis["commits"] = f"コミット分析: 期間中に合計 {commits_count} 件のコミットがありました。{commit_analysis['ja']}"
            analysis["pull_requests"] = f"プルリクエスト分析: 期間中に合計 {prs_count} 件のプルリクエストがありました。{pr_analysis['ja']}"
            analysis["total_contributions"] = f"総貢献分析: 期間中に合計 {total_contributions_count} 件の貢献がありました。{total_contributions_analysis['ja']} 貢献数はあなたの活動の総合的な指標であり、コミット、プルリクエスト、イシュー、レビューの合計を表しています。"

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
            analysis["total_contributions"] = f"Total Contributions Analysis: A total of {total_contributions_count} contributions were made during this period. {total_contributions_analysis['en']} The contribution count is a comprehensive metric of your activity, representing the sum of commits, pull requests, issues, and reviews."

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

    # The _create_bar_chart_data method has been removed as we're now using Chart.js

    def generate_html_report(self, user_data: Dict, output_path: Optional[str] = None) -> str:
        """
        Generate an HTML report with interactive charts.

        Args:
            user_data: Dictionary with user activity data
            output_path: Path where the HTML report will be saved

        Returns:
            Path to the generated HTML report
        """
        # No need to create Plotly chart data anymore as we're using Chart.js

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
            generation_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        # Save to file if output path is provided
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            return output_path

        return html_content
