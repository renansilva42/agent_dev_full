# setup/setup.py

from setuptools import setup, find_packages

setup(
    name="mam_project",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        # Flask and extensions
        "Flask>=3.0.2",
        "python-dotenv>=1.0.1",
        "Flask-Cors>=4.0.0",
        
        # OpenAI
        "openai>=1.12.0",
        
        # HTTP client
        "requests>=2.31.0",
        "httpx>=0.26.0",
        
        # Utilities
        "python-dateutil>=2.8.2",
        "pytz>=2024.1",
        
        # Development tools
        "black>=24.2.0",
        "flake8>=7.0.0",
        "pytest>=8.0.1",
        
        # Markdown processing
        "markdown>=3.5.2",
        "pygments>=2.17.2",
        
        # Security
        "python-jose>=3.3.0",
        "cryptography>=42.0.2",
        
        # CORS support
        "flask-cors>=4.0.0",
        
        # Session management
        "Flask-Session>=0.5.0",
        
        # Static file serving
        "whitenoise>=6.6.0",
        
        # Error handling
        "sentry-sdk>=1.40.4",
        
        # Logging
        "structlog>=24.1.0",
        
        # Environment variables
        "environs>=11.0.0",
        
        # Type hints
        "typing-extensions>=4.9.0",
        "mypy>=1.8.0"
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.1",
            "black>=24.2.0",
            "flake8>=7.0.0",
            "mypy>=1.8.0"
        ]
    },
    package_data={
        "mam_project": [
            "web_app/static/*",
            "web_app/static/styles.css",
            "web_app/static/index.html"
        ]
    },
    entry_points={
        "console_scripts": [
            "mam-project=mam_project.main:main"
        ]
    },
    python_requires=">=3.8",
    author="Your Name",
    author_email="your.email@example.com",
    description="Multi-Agent Model Project Analyzer",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    keywords="ai, analysis, code, project",
    url="https://github.com/yourusername/mam_project",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/mam_project/issues",
        "Documentation": "https://github.com/yourusername/mam_project/wiki",
        "Source Code": "https://github.com/yourusername/mam_project",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ]
)
