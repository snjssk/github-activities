from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="github-activities",
    version="0.1.0",
    author="GitHub Activities Team",
    author_email="example@example.com",
    description="A tool to track and display GitHub user activities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/github-activities",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "github-activities=github_activities.cli:main",
        ],
    },
)