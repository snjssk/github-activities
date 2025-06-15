# GitHub Activities Tracker

## Project Overview
This application fetches and displays GitHub user activities including:
- Commit counts
- Pull request numbers
- Issue creation counts
- Code review counts
- Other GitHub activity metrics

Data can be viewed in the terminal, exported as JSON, or visualized in HTML reports with interactive charts.

## Collaboration Information
If you're interested in collaborating on this project, here's what would be helpful to know:

### Technical Information
- **GitHub Username**: Your GitHub username to test the application
- **API Access**: Whether you have a GitHub personal access token
- **Development Environment**: Your preferred programming language and framework
- **Feature Priorities**: Which GitHub metrics are most important to you
- **UI Preferences**: Command-line interface or web/desktop application

### Project Structure
The project will be structured as follows:
- `src/`: Source code
- `config/`: Configuration files (including GitHub API tokens)
- `docs/`: Documentation
- `tests/`: Test files

### Technology Stack
We'll be using:
- Python for backend processing
- GitHub REST API v3 for data fetching
- Jinja2 for HTML templating
- Plotly for interactive data visualizations
- Rich for terminal UI

## Getting Started
1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Install the package: `pip install -e .`
4. Configure your GitHub API token (run `github-activities setup` or manually create config file)
5. Run the application: `github-activities summary <username>`
6. Export data as JSON: `github-activities export <username> --output data.json`
7. Generate HTML report with visualizations: `github-activities export <username> --format html --output report.html`

For detailed instructions in Japanese, see [日本語ガイド](docs/README_ja.md).

## Development Roadmap
1. ✅ Set up basic project structure
2. ✅ Implement GitHub API integration
3. ✅ Create data processing logic
4. ✅ Develop user interface
5. ✅ Add data visualization (HTML reports with interactive charts)
6. Implement user authentication (optional)

## License
[License information will be added]
