# mam_project/__init__.py

"""
Multi-Agent Model Project Analyzer
A system for analyzing and improving software projects using specialized AI agents.
"""

from .model import TransformerModel, OpenAIError
from .agents import (
    CodeAnalysisAgent,
    ProjectImprovementAgent,
    DatabaseAgent,
    BackendAgent,
    FrontendAgent,
    DevOpsAgent,
    ProjectManagementAgent,
    ResponseOptimizerAgent,
    RequestAnalyzerAgent
)
from .integration import IntegrationLayer, IntegrationError
from .web_app import create_app

__version__ = '1.0.0'
__author__ = 'Your Name'
__email__ = 'your.email@example.com'

__all__ = [
    'TransformerModel',
    'OpenAIError',
    'CodeAnalysisAgent',
    'ProjectImprovementAgent',
    'DatabaseAgent',
    'BackendAgent',
    'FrontendAgent',
    'DevOpsAgent',
    'ProjectManagementAgent',
    'ResponseOptimizerAgent',
    'RequestAnalyzerAgent',
    'IntegrationLayer',
    'IntegrationError',
    'create_app'
]

# Package metadata
metadata = {
    'name': 'mam_project',
    'version': __version__,
    'author': __author__,
    'author_email': __email__,
    'description': 'Multi-Agent Model Project Analyzer',
    'long_description': open('README.md').read(),
    'long_description_content_type': 'text/markdown',
    'url': 'https://github.com/yourusername/mam_project',
    'project_urls': {
        'Bug Tracker': 'https://github.com/yourusername/mam_project/issues',
        'Documentation': 'https://github.com/yourusername/mam_project/wiki',
        'Source Code': 'https://github.com/yourusername/mam_project',
    },
    'classifiers': [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ]
}
